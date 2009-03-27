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
"""Core Python Features

$Id$
"""
import os
import pkg_resources
from zope.interface import classImplements
from z3c.feature.core import interfaces, xml


class FileBasedTemplateBase(object):

    filename = None

    def getFeatures(self):
        if self.filename is None:
            raise ValueError("Missing filename attribute.")
        return xml.getFeaturesDict(open(self.filename))


def FileBasedTemplate(filename, title, description):
    FileBasedTemplate = type(
        '<FileBasedTemplate for %s' % filename,
        (FileBasedTemplateBase,), dict(title=title,
                                   description=description,
                                   filename=filename))

    classImplements(FileBasedTemplate, interfaces.IFileBasedTemplateProvider)
    return FileBasedTemplate


def getTemplateList():
    names = set()
    templates = {}
    for entryPoint in pkg_resources.working_set.iter_entry_points('z3c.boiler.template'):
        template = entryPoint.load()()
        if entryPoint.name in names:
            name = entryPoint.dist.project_name+':'+entryPoint.name
        else:
            name = entryPoint.name
        templates[name] = template
    return templates


def getTemplate(name):
    return getTemplateList()[name]

CommandLineProjectTemplate = FileBasedTemplate(
    os.path.join(os.path.dirname(__file__),"command-line-project.xml"),
    u"Command Line Program",
    u"Includes all the features you would want for a command line program.")

PythonPackageProjectTemplate = FileBasedTemplate(
    os.path.join(os.path.dirname(__file__),"python-package-project.xml"),
    u"Python Package",
    u"Just a simple python package with few bells and whistles.")
