##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test Helpers

$Id$
"""
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from z3c.builder.core import base

class TestingHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self, sys.stdout)

    def flush(self):
        self.stream = sys.stdout
        logging.StreamHandler.flush(self)

    def emit(self, record):
        self.stream = sys.stdout
        logging.StreamHandler.emit(self, record)


def formatDirListing(path):
    result = ''
    listing = os.listdir(path)
    files = filter(lambda x: os.path.isfile(os.path.join(path, x)), listing)
    files.sort()
    dirs = filter(lambda x: os.path.isdir(os.path.join(path, x)), listing)
    dirs.sort()
    result += '\n'.join(files)
    if dirs and files:
        result += '\n'
    for name in dirs:
        subPath = os.path.join(path, name)
        result += '%s/\n' % name
        result += '  '+formatDirListing(subPath).replace('\n','\n  ')
    return result

def ls(path, *args):
    path = os.path.join(path, *args)
    print formatDirListing(path)

def more(*args):
    path = os.path.join(*args)
    print open(path, 'r').read()

def clear(path):
    shutil.rmtree(path)
    os.mkdir(path)

def cmd(args, cwd):
    outputFilename = tempfile.mktemp()
    output = open(outputFilename, 'w')
    cmd = subprocess.Popen(args, cwd=cwd, stdout=output, stderr=output)
    status = cmd.wait()
    print 'Exit Status: ' + str(status)
    output.close()
    return open(outputFilename, 'r').read()

def buildSetUp(test):
    fn = tempfile.mktemp()
    test.globs.update(
        {'buildPath': fn,
         'cmd': cmd,
         'more': more,
         'ls':ls,
         'clear': clear})
    os.mkdir(fn)

def buildTearDown(test):
    shutil.rmtree(test.globs['buildPath'])

def loggerSetUp(test, level=logging.DEBUG, stream=None):
    test._oldLevel = base.logger.level
    if stream is None:
        test._handler = TestingHandler()
    else:
        test._handler = logging.StreamHandler(stream)
    base.logger.setLevel(level)
    base.logger.addHandler(test._handler)


def loggerTearDown(test):
    base.logger.setLevel(test._oldLevel)
    base.logger.removeHandler(test._handler)
