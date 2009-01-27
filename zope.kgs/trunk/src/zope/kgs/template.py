##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Helper components for the Web site generation.
"""
import os
import shutil
import zope.pagetemplate.pagetemplatefile

class Template(zope.pagetemplate.pagetemplatefile.PageTemplateFile):

    def __init__(self, path, templates):
        super(Template, self).__init__(path)
        self.templates = templates

    def pt_getContext(self, args=(), options=None, **ignore):
        rval = {'args': args,
                'nothing': None,
                'self': self,
                'templates': self.templates
                }
        rval.update(self.pt_getEngine().getBaseNames())
        return rval


class FileContext(object):

    def __init__(self, path, root):
        self.path = path
        self.root = root

    def __call__(self):
        pt = Template(self.path, self.root)
        return pt()


class DirectoryContext(object):

    def __init__(self, path, root=None):
        self.path = path
        self.root = root or self

    def __getitem__(self, name):
        path = os.path.join(self.path, name)
        if os.path.exists(path):
            return FileContext(path, self.root)
        return None


def generateSite(src, dst, data, templates=None):
    if templates is None:
        templates = DirectoryContext(src)
    for filename in os.listdir(src):
        srcPath = os.path.join(src, filename)
        dstPath = os.path.join(dst, filename)
        if filename.startswith('.'):
            continue
        elif srcPath.endswith('.pt'):
            continue
        elif os.path.isdir(srcPath):
            os.mkdir(dstPath)
            generateSite(srcPath, dstPath, data, templates)
        elif srcPath.endswith('.html'):
            data = Template(srcPath, templates)()
            open(dstPath, 'w').write(data)
        else:
            shutil.copyfile(srcPath, dstPath)
