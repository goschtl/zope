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
import copy
import zope.pagetemplate.pagetemplatefile

class Template(zope.pagetemplate.pagetemplatefile.PageTemplateFile):

    def __init__(self, path, data, templates):
        super(Template, self).__init__(path)
        self.templates = templates
        self.data = data

    def pt_getContext(self, args=(), options=None, **ignore):
        rval = self.data.copy()
        rval.update(
            {'args': args,
             'nothing': None,
             'self': self,
             'templates': self.templates,
             })
        rval.update(self.pt_getEngine().getBaseNames())
        return rval


class DirectoryContext(object):

    def __init__(self, path, data, root=None):
        self.path = path
        self.data = data
        self.root = root or self

    def __getitem__(self, name):
        path = os.path.join(self.path, name)
        if os.path.exists(path):
            return Template(path, self.data, self.root)
        return None


def generateSite(src, dst, data, templates=None):
    if templates is None:
        templates = DirectoryContext(src, data)
    for filename in os.listdir(src):
        srcPath = os.path.join(src, filename)
        dstPath = os.path.join(dst, filename)
        if filename.startswith('.'):
            continue
        elif srcPath.endswith('.pt'):
            continue
        elif srcPath.endswith('.html'):
            html = Template(srcPath, data, templates)()
            open(dstPath, 'w').write(html)
        elif filename == 'VERSION':
            for version in data['versions']:
                versionDir = os.path.join(dst, version['name'])
                newData = copy.deepcopy(data)
                newData['version'] = version
                newData['siteRoot'] = '../%s' % newData['siteRoot']
                generateSite(srcPath, versionDir, newData, templates)
        elif os.path.isdir(srcPath):
            if not os.path.exists(dstPath):
                os.mkdir(dstPath)
            newData = copy.deepcopy(data)
            newData['siteRoot'] = '../%s' % newData['siteRoot']
            generateSite(srcPath, dstPath, newData, templates)
        else:
            shutil.copyfile(srcPath, dstPath)
