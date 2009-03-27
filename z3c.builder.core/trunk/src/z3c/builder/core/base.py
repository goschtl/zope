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
"""Base Builder Components

$Id$
"""
import logging
import os
import uuid
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from zope.container import contained, ordered
from z3c.builder.core import interfaces

formatter = logging.Formatter('%(levelname)s - %(message)s')
logger = logging.getLogger('info')

def getTemplatePath(fn):
    return os.path.join(os.path.dirname(__file__), 'file-templates', fn)

def getUUID():
    return str(uuid.uuid4())

class ProjectGetter(object):
    zope.interface.implements(interfaces.IProjectGetter)

    def getProject(self):
        project = self
        while not interfaces.IProjectBuilder.providedBy(project):
            project = project.__parent__
            if project is None:
                raise ValueError(
                    'No project builder was found and the root node of '
                    'the project tree was reached.')
        return project


class BaseBuilder(contained.Contained):
    zope.interface.implements(interfaces.IBaseBuilder)

    name = FieldProperty(interfaces.IBaseBuilder['name'])

    def __init__(self, name):
        self.name = name

    def update(self):
        """See interfaces.IBaseBuilder"""
        logger.debug("Updating %s" %self)

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.name)


class BuilderContainer(BaseBuilder, ordered.OrderedContainer):
    zope.interface.implements(interfaces.IBuilderContainer)

    def __init__(self, name):
        super(BuilderContainer, self).__init__(name)
        ordered.OrderedContainer.__init__(self)

    def update(self):
        """See interfaces.IBaseBuilder"""
        super(BuilderContainer, self).update()
        for subBuilder in self.values():
            subBuilder.update()

    def add(self, builder):
        """See interfaces.IBuilderContainer"""
        self[builder.name] = builder
        return builder.name

    def remove(self, builder):
        """See interfaces.IBuilderContainer"""
        del self[builder.__name__]


class ContentBuilder(BaseBuilder, ProjectGetter):
    zope.interface.implements(interfaces.IContentBuilder)

    def render(self):
        """See interfaces.IContentBuilder"""
        raise NotImplementedError(
            "The `render()` method is not implemented by %s." %self)


class FilesystemBuilder(BaseBuilder, ProjectGetter):
    zope.interface.implements(interfaces.IFilesystemBuilder)

    def write(self, target):
        """See interfaces.IFilesystemBuilder"""
        raise NotImplementedError(
            "The `write(target)` method is not implemented.")


class DirectoryBuilder(FilesystemBuilder, BuilderContainer):
    zope.interface.implements(interfaces.IDirectoryBuilder)

    dirname = FieldProperty(interfaces.IDirectoryBuilder['dirname'])

    def __init__(self, name, dirname=None):
        super(DirectoryBuilder, self).__init__(name)
        # Use the builder name as the default directory name.
        if dirname is None:
            dirname = str(name)
        self.dirname = dirname

    def write(self, target):
        """See interfaces.IFilesystemBuilder"""
        dirpath = os.path.join(target, self.dirname)
        logger.info("Creating directory %s" % dirpath)
        os.mkdir(dirpath)
        for subBuilder in self.values():
            subBuilder.write(dirpath)


class FileBuilder(FilesystemBuilder):
    zope.interface.implements(interfaces.IFileBuilder)

    filename = FieldProperty(interfaces.IFileBuilder['filename'])

    def __init__(self, name, filename=None):
        super(FileBuilder, self).__init__(name)
        if filename is None:
            filename = str(name)
        self.filename = filename

    def render(self):
        """See interfaces.IContentBuilder"""
        raise NotImplementedError("The `render()` method is not implemented.")

    def write(self, target):
        """See interfaces.IFilesystemBuilder"""
        filepath = os.path.join(target, self.filename)
        logger.info("Creating file %s" % filepath)
        file = open(filepath, 'w')
        file.write(self.render())
        file.close()


class SimpleFileBuilder(FileBuilder):

    def __init__(self, name, template, filename=None):
        super(SimpleFileBuilder, self).__init__(name, filename)
        self.template = template

    def render(self):
        """See interfaces.IContentBuilder"""
        return open(self.template, 'r').read()
