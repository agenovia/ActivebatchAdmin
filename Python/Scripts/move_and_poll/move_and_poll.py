"""
Copy files that match a certain regex pattern from a source to a destination and poll every N seconds for a total of T
seconds until the file with the same pattern shows up in the destination. Exit with the specified TimeOut code
(default 1) or SuccessCode (default 0)

CAUTION: If the Regex provided does not have a capturing group, then the Regex must match 1:1 from source file to
poll file. This was done to address a use case with outbound 834 files that have their name modified by the BizTalk
process and so a fuzzy match has to be performed. The way I have implemented it makes this script very generic whilst
allowing for the particular use case to be performed easily
"""
import logging
import re
import time
from argparse import ArgumentParser
from os import scandir
from shutil import copy


def parse_arguments(args):
    parser = ArgumentParser()
    parser.add_argument('--SourceFolder',
                        required=True,
                        help='This is the folder to look for files. There can be multiple files and their filename '
                             'must be specified in the regex',
                        type=str,
                        )
    parser.add_argument('--DestinationFolder',
                        required=True,
                        help='This is the folder to place the files in',
                        type=str
                        )
    parser.add_argument('--PollFolder',
                        required=True,
                        help='This is the folder to poll',
                        type=str
                        )
    parser.add_argument('--Regex',
                        required=True,
                        help='This is the regex to look for. Any groups specified in the regex must match source to '
                             'destination',
                        type=str
                        )
    parser.add_argument('--Timeout',
                        required=False,
                        default=300,
                        help='If the timeout has been exceeded, the script will exit with the TimeoutCode provided or '
                             'the default value of 1. TimeOut has a default value of 300 seconds',
                        )
    parser.add_argument('--PollInterval',
                        required=False,
                        help='Poll at an interval specified by this parameter',
                        default=5
                        )
    parser.add_argument('--TimeoutCode',
                        required=False,
                        default=1,
                        help='If specified, then this code will be used to exit on a TimeOut',
                        )
    parser.add_argument('--SuccessCode',
                        required=False,
                        default=0,
                        help='If specified, then this code will be used to exit on a Successful operation',
                        )
    return parser.parse_args(args)


class MoveAndPoll(object):
    def __init__(self, source_dir, destination_dir, poll_folder, regex, timeout, poll_interval, timeout_code,
                 success_code):
        self.source_dir = source_dir
        self.destination_dir = destination_dir
        self.poll_folder = poll_folder
        self.regex = regex
        self.reg = re.compile(regex, re.IGNORECASE)
        self.timeout = int(timeout)
        self.poll_interval = int(poll_interval)
        self.timeout_code = int(timeout_code)
        self.success_code = int(success_code)

        logging.debug(self.__repr__())

    def __repr__(self):
        return f"MoveAndPoll(source_dir={self.source_dir}, destination_dir={self.destination_dir}, " \
               f"poll_folder={self.poll_folder}, regex={self.regex}, timeout={self.timeout}, " \
               f"poll_interval={self.poll_interval}, timeout_code={self.timeout_code}, success_code={self.success_code})"

    def reg(self):
        pass

    def copy_to_destination(self) -> list:
        """
        Copy files matching a specified regex pattern to from a source directory to a destination directory, return the
        list of source files and the compiled regex
        :return:
        """
        source_files = [file for file in scandir(self.source_dir) if self.reg.match(file.name)]
        _sources = [file.path for file in source_files]
        logging.info(f"Found {len(source_files)} files: {_sources}")
        for file in source_files:
            try:
                logging.info(f"Copying {file.name} from {file.path} to {self.destination_dir}")
                copy(file.path, self.destination_dir)
            except Exception as e:
                logging.exception(e, exc_info=True)  # recapturing in case I want to pipe the logging handler to files
                logging.debug(f"Exception in attempting to move {file.name} from {file.path} to {self.destination_dir}")
                raise

        return source_files

    def poll(self) -> int:
        """
        Perform a poll of N poll_interval for a maximum of T timeout. Return TimeOut code if no file appears in the
        destination in the allotted time, else return SuccessCode
        :return:
        """
        source_files = self.copy_to_destination()

        # while timeout has not been exceeded
        end = time.time() + self.timeout

        _polling = [file.name for file in source_files]
        try:
            src_keywords = [self.reg.search(fname).group(1) for fname in [file.name for file in source_files] if
                            self.reg.match(fname)]
        except IndexError:
            src_keywords = [fname for fname in [file.name for file in source_files] if self.reg.match(fname)]

        logging.info(f"Waiting for {src_keywords} to appear in {self.poll_folder}")
        while time.time() <= end:
            try:
                poll_files = [file for file in scandir(self.poll_folder) if self.reg.match(file.name)]
            except Exception as e:  # in case I lose connection to the place I need to check before the script finishes
                logging.exception(e, exc_info=True)
                logging.debug(f"Exception in attempting to poll the {self.poll_folder} location. Please investigate potential network outages")
                raise
            try:
                poll_keywords = [self.reg.search(fname).group(1) for fname in [file.name for file in poll_files] if self.reg.match(fname)]
            except IndexError:
                poll_keywords = [fname for fname in [file.name for file in poll_files] if self.reg.match(fname)]
            # for file in source_files, do they appear in poll_files
            _matches = [_src in poll_keywords for _src in src_keywords]
            if all(_matches):
                logging.info(f"All patterns expected from '{self.source_dir}' ({src_keywords}) using the regex pattern '{self.regex}' have been found in '{self.poll_folder}'")
                return self.success_code
            else:
                logging.debug(f"timeout: {end - time.time():.0f} seconds -- poll rate: {self.poll_interval} seconds")
                time.sleep(self.poll_interval)

        return self.timeout_code


if __name__ == '__main__':
    pass
