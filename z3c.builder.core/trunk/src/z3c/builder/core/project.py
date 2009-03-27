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
"""Representation of a Python Project

$Id$
"""
import os
import shutil
import zope.interface
from rwproperty import getproperty
from zope.schema.fieldproperty import FieldProperty

from z3c.builder.core import base, buildout, interfaces, python, setup


class ProjectBuilder(base.DirectoryBuilder):
    zope.interface.implements(interfaces.IProjectBuilder)

    projectName = FieldProperty(interfaces.IProjectBuilder['projectName'])
    commentHeader = FieldProperty(interfaces.IProjectBuilder['commentHeader'])

    def __init__(self, name, projectName=None):
        super(ProjectBuilder, self).__init__(name)
        if projectName is None:
            projectName = str(name)
        self.projectName = self.dirname = projectName
        self.commentHeader = unicode(open(
            base.getTemplatePath('gpl3-header.py'), 'r').read())


    def update(self):
        self.directoryPath = unicode(self.name)
        self.commentHeader = self.commentHeader %self.__dict__
        for builder in self.values():
            builder.update()

    def write(self, target, force=False):
        """See interfaces.IProjectBuilder"""
        dirPath = os.path.join(target, self.dirname)
        if os.path.exists(dirPath):
            if not force:
                raise interfaces.FileExistsException(dirPath)
            shutil.rmtree(dirPath)
        super(ProjectBuilder, self).write(target)


class BuildoutProjectBuilder(ProjectBuilder):
    zope.interface.implements(interfaces.IBuildoutProjectBuilder)

    @getproperty
    def setup(self):
        return self['setup.py']

    @getproperty
    def buildout(self):
        return self['buildout.cfg']

    @getproperty
    def package(self):
        return self['src'].package

    def __init__(self, name, projectName=None):
        super(BuildoutProjectBuilder, self).__init__(name, projectName)
        # Create the minimum amount files necessary to build a valid project
        self['bootstrap.py'] = base.SimpleFileBuilder(
            u'bootstrap.py', base.getTemplatePath('bootstrap.py'))
        self['setup.py'] = setup.SetupBuilder()
        self['buildout.cfg'] = buildout.BuildoutConfigBuilder()
        self['src'] = SrcDirectoryBuilder()
        self['src'].updateModules(self.name)


class SrcDirectoryBuilder(base.DirectoryBuilder):

    zope.interface.implements(interfaces.IPythonPathRoot)

    def __init__(self):
        super(SrcDirectoryBuilder, self).__init__(u'src')
        self.package = python.PackageBuilder(u'')

    def updateModules(self, projectName):
        modules = list(reversed(unicode(projectName).split('.')))
        builder = self
        while len(modules) > 0:
            name = modules.pop()
            nextBuilder = python.PackageBuilder(name)
            if len(modules) == 0:
                nextBuilder = self.package
                nextBuilder.dirname = nextBuilder.packageName = str(name)
                nextBuilder.name = name
            builder.add(nextBuilder)
            builder = nextBuilder

    def update(self):
        for builder in self.values():
            builder.update()

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.getProject().name)
