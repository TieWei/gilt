# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import contextlib
import errno
import os
import shutil
import sys
import threading

import colorama

colorama.init(autoreset=True)
_lock = threading.Lock()
_named_locks = {}


def print_info(msg):
    """ Print the given message to STDOUT. """
    with _lock:
        print msg
        sys.stdout.flush()


def print_warn(msg):
    """ Print the given message to STDOUT in YELLOW. """
    with _lock:
        print '{}{}'.format(colorama.Fore.YELLOW, msg)
        sys.stdout.flush()


@contextlib.contextmanager
def named_lock(name):
    with _lock:
        if name not in _named_locks:
            _named_locks[name] = threading.Lock()
    with _named_locks[name]:
        yield


def run_command(cmd, debug=False):
    """
    Execute the given command and return None.

    :param cmd: A `sh.Command` object to execute.
    :param debug: An optional bool to toggle debug output.
    :return: None
    """
    if debug:
        msg = '  PWD: {}'.format(os.getcwd())
        print_warn(msg)
        msg = '  COMMAND: {}'.format(cmd)
        print_warn(msg)
    cmd()


@contextlib.contextmanager
def saved_cwd():
    """ Context manager to restore previous working directory. """
    saved = os.getcwd()
    try:
        yield
    finally:
        os.chdir(saved)


def copy(src, dst):
    """
    Handle the copying of a file or directory.

    The destination basedir _must_ exist.

    :param src: A string containing the path of the source to copy.  If the
     source ends with a '/', will become a recursive directory copy of source.
    :param dst: A string containing the path to the destination.  If the
     destination ends with a '/', will copy into the target directory.
    :return: None
    """
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise
