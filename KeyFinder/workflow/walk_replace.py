#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import re
import json
import traceback

from KeyFinder.comm.global_setup import show_progress
from KeyFinder.comm.logger import logger


class WalkReplaceWorkflow(object):

    class __ReplaceSchema(object):

        def __init__(self):
            self.rep_file_type = list()
            self.rep_files = list()
            self.rep_data = list()

    def __init__(self, *args):
        """
        Init Function

        :param args: Input parameters, passed through mechanic engine, type: tuple
        :param kwargs: Input parameters, passed through mechanic engine, type: dict
        """
        (self.path, self.keyword) = args
        self.rep_schema = self.__ReplaceSchema()
        self.user_file_list = list()
        self.res_file_list = list()
        self.result_file = "{}/result.json".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.result_data = dict()
        self.read_replace_schema(self.rep_schema)
        self.read_result_data()

    def __enter__(self):
        """
        Enter function will implement after __init__

        :return: self, type: object
        """
        self.user_file_list = self.collect_schema_replace_files()
        self.res_file_list = self.collect_result_key_file_list()
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

    @classmethod
    def read_replace_schema(cls, obj_schema):
        logger.info("Reading replace schema...")
        schema_file = "{}/replace_schema.json".format(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(schema_file, "rt") as fr:
            schemas = json.loads(fr.read())
            obj_schema.rep_file_type = schemas.get("rep_file_type")
            obj_schema.rep_files = schemas.get("rep_files")
            obj_schema.rep_data = schemas.get("rep_data")
            fr.close()

    def read_result_data(self):
        logger.info("Reading search result file data...")
        with open(self.result_file, "rt") as fr:
            self.result_data = json.loads(fr.read())
            fr.close()

    def schema_walk_file_list(self, path):
        logger.debug("Walking target path: %s" % path)
        if os.path.isfile(path):
            [self.user_file_list.append(path) for ftype in self.rep_schema.rep_file_type
             if os.path.splitext(path)[-1] == ftype]
        elif os.path.isdir(path):
            for sub_dir in os.listdir(path):
                new_dir = os.path.join(path, sub_dir)
                self.schema_walk_file_list(new_dir)

    def collect_schema_replace_files(self):
        logger.info("Collecting replace file list according to schema...")
        if self.rep_schema.rep_files:
            logger.warning("Will only walk user specify replace files schema: %s" % self.rep_schema.rep_files)
            [self.schema_walk_file_list(path) for path in self.rep_schema.rep_files]
        else:
            self.schema_walk_file_list(self.path)
        return list(set(self.user_file_list))

    def collect_result_key_file_list(self):
        logger.info("Collecting replace file list according to result...")
        for key in self.keyword:
            for res_entry in self.result_data.get(key):
                res_key = list(res_entry.keys())[0]
                [self.res_file_list.extend(res_entry[list(rep_entry.keys())[0]]) for rep_entry
                 in self.rep_schema.rep_data if res_key == list(rep_entry.keys())[0]]
        return list(set(self.res_file_list))

    def update_walk_replace(self):
        def replace_target_value(src, tgt):
            file_size = len(update_files)
            for index, file in enumerate(update_files):
                show_progress(index, file_size)
                with open(file, "rt") as fr:
                    content = fr.readlines()
                    fr.close()
                with open(file, "wt") as fw:
                    [fw.writelines(re.sub(src, tgt, entry)) for entry in content]
                    fw.close()

        logger.info("Updating target file for schema data...")
        # Default result file list
        update_files = list(set(self.res_file_list))
        # User specify file types, it must a sub set of result file list
        if self.rep_schema.rep_file_type:
            logger.warning("Will only replace user specify file types schema: %s" % self.rep_schema.rep_file_type)
            update_files = list(set(self.user_file_list) & set(self.res_file_list))
        for rep_data in self.rep_schema.rep_data:
            [replace_target_value(key, value) for key, value in rep_data.items()]
