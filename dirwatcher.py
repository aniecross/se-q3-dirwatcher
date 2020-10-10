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

stay_running = True
files_logged = []
found_magic_string = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(message)s')
file_handler = logging.FileHandler("dirwatcher.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def search_for_magic(filename, start_line, magic_string):
    """searches file for a line containing magic_string"""
    with open(filename) as doc:
        content = doc.readlines()
        for line_number, line in enumerate(content):
            if magic_string in line:
                if filename not in found_magic_string.keys():
                    found_magic_string[filename] = line_number
                if (line_number >= found_magic_string[start_line]) and start_line in found_magic_string.keys():
                    logger.info("Match found for {} found on line {} in {}".format(magic_, line_number + 1, start_line))
                    found_magic_string[start_line] += 1


def watch_directory(path, magic_string, extension, interval):
    """Watches directory for instances of a magic string"""
    global files_logged
    global found_magic_string

    try:
        text_files = [f for f in os.listdir(directory) if not f.startswith('.')]
    except:
        logger.info('Directory {} does not exists'.format(directory))
    else:
        abspath = os.path.abspath(directory)
        files = os.listdir(abspath)
        for file in text_files:
            if file.endswith(ext) and file not in files_logged:
                logger.info('New file found: {}'.format(file))
                files_logged.append(file)
            if file.endswith(ext):
                full_path = os.path.join(abspath, file)
                if search_single_file(full_path, magic_string):
                    break
        for file in files_logged:
            if file not in files:
                logger.info('File deleted: {}'.format(file))
                files_logged.remove(file)
                found_magic_string[file] = 0


def create_parser():
    parser = argparse.ArgumentParser(description='Watches a directory for files containing magic string')
    parser.add_argument('-i', '--int', help='Polling interval for program')
    parser.add_argument('-e', '--ext', help='Extension of file to search for', default=".txt")
    parser.add_argument('path', help='Directory to be searched', default= ".")
    parser.add_argument('magic', help='Magic string to be found in files')
    return parser


def signal_handler(sig_num, frame):
    global stay_running
    sigs = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warning('Received OS Signal: {}'.format(sigs[sig_num]))

    stay_running = False


def main(args):
    start_time = time.time()
    parser = create_parser()
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    """function for finding magic word"""
    logger.info("Watching directory {} for files ending with {} containing magic string {}".format(args.path, args.ext, args.magic))
    while stay_running:
        try:
            find_magic_word(args.path, args.magic, args.ext)
        except Exception:
            logger.exception("exception on main")
        time.sleep(float(args.int))
        logger.info("Program uptime: {} seconds".format(time.time() - start_time))


if __name__ == '__main__':
    main(sys.argv[1:])
