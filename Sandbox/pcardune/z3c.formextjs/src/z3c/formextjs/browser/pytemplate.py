##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Simple Python Template Engine.

$Id$
"""
import os.path, sys

def package_home(gdict):
    filename = gdict["__file__"]
    return os.path.dirname(filename)

class PythonTemplateFile(object):

    def __init__(self, filename, _prefix=None):
        path = self.get_path_from_prefix(_prefix)
        self.filename = os.path.join(path, filename)
        if not os.path.isfile(self.filename):
            raise ValueError("No such file", self.filename)

    def get_path_from_prefix(self, _prefix):
        if isinstance(_prefix, str):
            path = _prefix
        else:
            if _prefix is None:
                _prefix = sys._getframe(2).f_globals
            path = package_home(_prefix)
        return path

    def __call__(self, context, **kwargs):
        inFile = open(self.filename, 'rb')
        scope = {'r':'', 'context':context}
        scope.update(kwargs)
        exec inFile in scope
        return scope['r']
