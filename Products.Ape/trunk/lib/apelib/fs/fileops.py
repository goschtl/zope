##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Filesystem I/O abstraction.

$Id$
"""

import os
import shutil


class StandardFileOperations:
    """Standard filesystem interaction implementation.

    Provides the operations needed by FSConnection.
    """

    def __init__(self):
        self.dirname = os.path.dirname
        self.exists = os.path.exists
        self.getmtime = os.path.getmtime
        self.isdir = os.path.isdir
        self.join = os.path.join
        self.listdir =  os.listdir
        self.makedirs = os.makedirs
        self.mkdir = os.mkdir
        self.remove = os.remove
        self.rename = os.rename
        self.rmtree = shutil.rmtree
        self.split = os.path.split
        self.splitext = os.path.splitext
        
    def readfile(self, path, as_text):
        f = open(path, as_text and 'rt' or 'rb')
        try:
            return f.read()
        finally:
            f.close()

    def writefile(self, path, as_text, bytes):
        f = open(path, as_text and 'wt' or 'wb')
        try:
            f.write(bytes)
        finally:
            f.close()

    def canwrite(self, path):
        return os.access(path, os.W_OK)

