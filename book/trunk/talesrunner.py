##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""TALES runner

$Id: talesrunner.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
import os, sys
from zope.tales.engine import Engine
from zope.tales.tales import Context

class Directory(object):

    def __init__(self, path):
        self.path = path
        self.filename = os.path.split(path)[1]

    def __getitem__(self, key):
        path = os.path.join(self.path, key)
        if not os.path.exists(path):
            raise KeyError, "No file '%s' in '%s'" %(key, self.filename)
        elif os.path.isdir(path):
            value = Directory(path)
        else:
            value = File(path)
        return value
        
    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def keys(self):
        return os.listdir(self.path)

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def values(self):
        return [value for key, value in self.items()]
        

class File(object):
    
    def __init__(self, path):
        self.path = path
        self.filename = os.path.split(path)[1]

    def read(self):
        return open(self.path, 'r').read()

if __name__ == '__main__':
    path = sys.argv[1]
    context = Context(Engine, {'root': Directory(path)})
    while 1 == 1:
        expr = raw_input("TALES Expr: ")
        if expr == 'exit':
            break
        try:
            bytecode = Engine.compile(expr)
            print bytecode(context)
        except Exception, error:
            print error
