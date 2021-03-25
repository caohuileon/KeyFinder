#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import sys
import os

# This line is used for deploy to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from KeyFinder.comm.logger import logger
from KeyFinder.workflow import walk_keyword, walk_replace


def get_args():
    """
    This function is parse user CLI input values, it supports components level

    :return: The args user input, type: object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", required=True, type=str, metavar="<Find Keywords>",
                        help="What keywords you want to walk.")
    parser.add_argument("-p", "--path", required=True, type=str, metavar="<Walk Path>", help="Input walk path.")
    parser.add_argument("-b", "--branch", type=str, metavar="<Git Branch>", help="Choose git repo branch.")
    parser.add_argument("--replace", type=str, metavar="<True|False>", choices=["True", "False"], default=False,
                        help="A json file store replace content. Default: [False]")
    args = parser.parse_args()
    return args


def show_title_info(key, path, branch, replace):
    logger.info("============================================ Task Begin =============================================")
    logger.info("Keyword: %s, Path: %s, Branch: %s, Replace: %s" % (key, path, branch, replace))
    logger.info("=====================================================================================================")


def show_end_info(key, path, branch, replace):
    logger.info("============================================= Task End ==============================================")
    logger.info("Keyword: %s, Path: %s, Branch: %s, Replace: %s" % (key, path, branch, replace))
    logger.info("=====================================================================================================")


def change_directory(path):
    logger.info("Changing work directory to: %s" % path)
    try:
        os.chdir(path)
    except FileNotFoundError as err:
        raise RuntimeError("Cannot change to path: %s with err: %s" % (path, err))


def perform_checkout_branch(branch):
    logger.info("Performing checkout branch...")
    if os.system("git checkout {}".format(branch)):
        logger.error("Checkout branch failed, please check branch name!")
        raise RuntimeError("Checkout branch failed, please check branch name!")


def perform_walk_keyword(path, keyword):
    logger.info("Performing walk keyword...")
    with walk_keyword.WalkKeyWorkflow(path, keyword) as walk_key:
        walk_key.save_walk_data()


def perform_replace(path, keyword):
    logger.info("Performing replace user data...")
    with walk_replace.WalkReplaceWorkflow(path, keyword) as walk_rep:
        walk_rep.update_walk_replace()


def main():
    args = get_args()
    # Remove duplicated items
    keyword = list(set(args.key.split(",")))
    path = args.path
    branch = args.branch
    replace = args.replace
    show_title_info(keyword, path, branch, replace)
    change_directory(path)
    if branch:
        perform_checkout_branch(branch)
    perform_walk_keyword(path, keyword)
    if replace:
        perform_replace(path, keyword)
    show_end_info(keyword, path, branch, replace)


if __name__ == '__main__':
    main()
