#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import json
import subprocess
import traceback

from KeyFinder.comm.logger import logger
from KeyFinder.comm.global_setup import REGEX_IP, show_progress


class WalkKeyWorkflow(object):

    def __init__(self, *args):
        """
        Init Function

        :param args: Input parameters, passed through mechanic engine, type: tuple
        :param kwargs: Input parameters, passed through mechanic engine, type: dict
        """
        (self.path, self.keyword) = args
        self.file_list = list()
        self.all_ip_map = list()
        self.result = dict()

    def __enter__(self):
        """
        Enter function will implement after __init__

        :return: self, type: object
        """
        self.build_description()
        self.walk_file_list(self.path)
        self.walk_keyword(self.keyword)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit function will process error messages

        :param exc_type: error trace type
        :param exc_val: error trace value
        :param exc_tb: error trace traceback
        :return: True, it will continue to the next component, type: bool
        """
        logger.info("Processing error message...")
        # Print job errors after "with xx as xx:" part
        if any([exc_type, exc_val, exc_tb]):
            traceback.print_exception(exc_type, exc_val, exc_tb)
            logger.info(traceback.extract_tb(exc_tb))
        else:
            logger.info("None")
        # Based on your requirements to set True or remove return
        return True

    def build_description(self):
        logger.info("Generating description info...")
        self.result["description"] = dict()
        self.result["description"]["keyword"] = self.keyword
        self.result["description"]["path"] = self.path
        ret = subprocess.check_output(r"cd {} && git branch | grep \*".format(self.path), shell=True)
        self.result["description"]["branch"] = ret.decode().strip(r"* ").strip()

    def walk_file_list(self, path):
        logger.debug("Walking target path: %s..." % path)
        if os.path.isfile(path):
            self.file_list.append(path)
        elif os.path.isdir(path):
            for sub_dir in os.listdir(path):
                new_dir = os.path.join(path, sub_dir)
                self.walk_file_list(new_dir)

    def walk_keyword(self, keys):
        logger.info("Walking keyword: %s in total file: %s" % (keys, len(self.file_list)))
        for key in keys:
            if key.lower() == "all ip":
                self.result[key] = self.search_all_ip_address()
            elif "*" in key:
                self.result[key] = self.blur_search_key(key)
            else:
                self.result[key] = self.exact_search_key(key)

    def search_all_ip_address(self):
        def map_ip_file(ipls, filels):
            ipls.sort()
            map_list = list()
            for sip in ipls:
                # Combine all same ip key
                map_list.append({sip: list(set([item[sip] for item in filels if sip in item.keys()]))})
            return map_list

        logger.info("Searching all ip address mapping...")
        ip_list = list()
        ip_file = list()
        file_size = len(self.file_list)
        for index, file in enumerate(self.file_list):
            show_progress(index, file_size)
            try:
                with open(file, "rt") as fr:
                    # Do not use readlines() since here might more than 2 ips in one line, and re.search() only
                    # returns the first match.
                    content = fr.read().split()
                    for entry in content:
                        ip = re.search(REGEX_IP, entry)
                        if ip is not None:
                            logger.debug("Get IP: %s in file: %s" % (ip.group(), file))
                            ip_list.append(ip.group())
                            ip_file.append({ip.group(): file})
            except (IOError, UnicodeDecodeError) as err:
                logger.warning("Ignore error: %s in file: %s" % (err, file))
                continue
        self.all_ip_map = map_ip_file(list(set(ip_list)), ip_file)
        return self.all_ip_map

    def collect_key_list(self, keyword):
        logger.info("Collecting ip key list...")
        key_list = list()
        self.all_ip_map if self.all_ip_map else self.search_all_ip_address()
        # Use str(entry.keys()) to quick compare key_ip string
        [key_list.append(entry) for entry in self.all_ip_map if keyword in str(entry.keys())]
        return key_list

    def collect_none_ip_key_list(self, keyword):
        logger.info("Collecting none ip key list...")
        key_list = list()
        file_size = len(self.file_list)
        for index, file in enumerate(self.file_list):
            show_progress(index, file_size)
            try:
                with open(file, "rt") as fr:
                    # Use readlines() to check none-ip keyword will be faster
                    content = fr.readlines()
                    for entry in content:
                        if keyword in entry:
                            logger.debug("Get Keyword: %s in file: %s" % (keyword, file))
                            key_list.append(file)
            except (IOError, UnicodeDecodeError) as err:
                logger.warning("Ignore error: %s in file: %s" % (err, file))
                continue
        # return to keep same structure as ip mapping result, so add [{}]
        return [{keyword: list(set(key_list))}]

    def blur_search_key(self, keyword):
        logger.info("Blur searching keyword mapping...")
        # Judge user input is a blur IP address search
        if "".join(re.split("[.*]", keyword)).isnumeric():
            key_ip = keyword.strip("*")
            return self.collect_key_list(key_ip)
        # Else user input is a none IP keywords
        key_wd = keyword.strip("*")
        return self.collect_none_ip_key_list(key_wd)

    def exact_search_key(self, keyword):
        logger.info("Exact searching keyword mapping...")
        # Judge user input is a blur IP address search
        if "".join(keyword.split(".")).isnumeric():
            return self.collect_key_list(keyword)
        # Else user input is a none IP keywords
        return self.collect_none_ip_key_list(keyword)

    def save_walk_data(self):
        res_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logger.info("Saving searching result to path: %s/result.json" % res_path)
        with open("{}/result.json".format(res_path), "wt") as fw:
            fw.write(json.dumps(self.result, indent=2, separators=(',', ': ')))
            fw.close()
