#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = """Anie Cross with help from instructor demo recordings, Google search,
docs.python.org, stackoverflow.com, reviewed codes from github.com/dougenas/dirwatcher,
and from github.com/Mharsley/backend-dirwatcher/blob/dev"""

import os
import sys
import argparse
import logging
import signal
import time
from os.path import isfile, join, splitext

stay_running = True
files_logged = {}
found_magic_string = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(message)s')
# file_handler = logging.FileHandler("dirwatcher.log")
# file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def search_for_magic(file_path, filename, start_line, magic_string):
    """searches file for a line containing magic_string"""
    current_line = 1
    with open(file_path) as doc:
        for line in doc:
            if current_line >= start_line:
                if magic_string in line:   
                    logger.info(f"Magic text found on line {current_line} in {filename}") 
                current_line += 1
    files_logged[filename] = current_line


def watch_directory(directory, magic_string, extension):
    """Watches directory for instances of a magic string"""
    global files_logged
    global found_magic_string
    files_to_remove = []

    try:
        text_files = [f for f in os.listdir(directory) if isfile(join(directory, f))]
        logger.info(text_files)
    except OSError as err:
        logger.error('Directory {} does not exists'.format(directory))
    else:
        abspath = os.path.abspath(directory)
        files = os.listdir(abspath)
        for file in text_files:
            file_name, file_ext = splitext(file)
            if file_ext == extension and file not in files_logged:
                logger.info('New file found: {}'.format(file))
                files_logged[file] = 0
        for file in files_logged.keys():
            if file not in files:
                logger.info('File deleted: {}'.format(file))
                files_to_remove.append(file)
        for file in files_to_remove:
            del files_logged[file]
        for k, v in files_logged.items():
            file_path = join(directory, k)
            search_for_magic(file_path, k, v, magic_string)         


def create_parser():
    """Parser to add command line arguments"""
    parser = argparse.ArgumentParser(description='Watches a directory for files containing magic string')
    parser.add_argument('-i', '--int', help='Polling interval for program')
    parser.add_argument('-e', '--ext', help='Extension of file to search for', default=".txt")
    parser.add_argument('path', help='Directory to be searched', default= ".")
    parser.add_argument('magic', help='Magic string to be found in files')
    return parser


def signal_handler(sig_num, frame):
    """function that waits for OS interupt"""
    global stay_running
    sigs = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warning('Received OS Signal: {}'.format(sigs[sig_num]))

    stay_running = False


def main(args):
    start_time = time.time()
    parser = create_parser()
    ns = parser.parse_args(args)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    """function for finding magic word"""
    logger.info("Watching directory {} for files ending with {} containing magic string {}".format(ns.path, ns.ext, ns.magic))
    while stay_running:
        try:
            watch_directory(ns.path, ns.magic, ns.ext)
        except Exception:
            logger.exception("exception on main")
        time.sleep(float(ns.int))
        logger.info("Program uptime: {} seconds".format(time.time() - start_time))


if __name__ == '__main__':
    main(sys.argv[1:])
