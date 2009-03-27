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
"""Representation of the setup.py file.

$Id$
"""
import types
import pprint
import zope.interface
from rwproperty import getproperty
from zope.schema.fieldproperty import FieldProperty
from zope.container.sample import SampleContainer
from zope.container.contained import Contained
from zope.location.location import locate

from z3c.builder.core import base, buildout, interfaces

class SetupBuilder(base.FileBuilder):
    zope.interface.implements(interfaces.ISetupBuilder)

    version = FieldProperty(interfaces.ISetupBuilder['version'])
    license = FieldProperty(interfaces.ISetupBuilder['license'])
    author = FieldProperty(interfaces.ISetupBuilder['author'])
    author_email = FieldProperty(interfaces.ISetupBuilder['author_email'])
    description = FieldProperty(interfaces.ISetupBuilder['description'])
    keywords = FieldProperty(interfaces.ISetupBuilder['keywords'])
    url = FieldProperty(interfaces.ISetupBuilder['url'])
    classifiers = FieldProperty(
        interfaces.ISetupBuilder['classifiers'])
    namespace_packages = FieldProperty(
        interfaces.ISetupBuilder['namespace_packages'])
    install_requires = FieldProperty(
        interfaces.ISetupBuilder['install_requires'])
    extras_requires = FieldProperty(
        interfaces.ISetupBuilder['extras_require'])
    entry_points = FieldProperty(
        interfaces.ISetupBuilder['entry_points'])

    def __init__(self):
        super(SetupBuilder, self).__init__(u'setup.py')
        self.keywords = []
        self.namespace_packages = []
        self.install_requires = []
        self.classifiers = []
        self.extras_requires = {}
        self.entry_points = {}

    def addExtrasRequires(self, name, requirements):
        """See interfaces.ISetupBuilder"""
        self.extras_requires.setdefault(name, [])
        self.extras_requires[name] = list(
            set(self.extras_requires[name]).union(requirements))

    def removeExtrasRequires(self, name):
        """See interfaces.ISetupBuilder"""
        del self.extras_requires[name]

    def addEntryPoints(self, name, entries):
        """See interfaces.ISetupBuilder"""
        self.entry_points.setdefault(name, [])
        self.entry_points[name] = list(
            set(self.entry_points[name]).union(entries))

    def removeEntryPoints(self, name):
        """See interfaces.ISetupBuilder"""
        del self.entry_points[name]

    def update(self):
        """See interfaces.IBaseBuilder"""
        project = self.getProject()
        if not self.url:
            self.url = u'http://pypi.python.org/pypi/%s' % project.name
        # Update the namespace packages.
        if not self.namespace_packages:
            pieces = project.name.split('.')[:-1]
            pieces.reverse()
            ns = []
            while pieces:
                ns.append(pieces.pop())
                self.namespace_packages.append('.'.join(ns))

    def render(self):
        """See interfaces.IContentBuilder"""
        template = open(base.getTemplatePath('setup.py'), 'r').read()
        project = self.getProject()
        data = dict(
            commentHeader=project.commentHeader.strip(),
            name=project.name,
            version=self.version,
            license=self.license,
            author=self.author,
            author_email=self.author_email,
            description=self.description,
            url=self.url,
            keywords=' '.join(self.keywords),
            namespacePackages='',
            )
        if self.namespace_packages:
            data['namespacePackages'] = ','.join(
                map(repr, self.namespace_packages))

        requirementsStr = ''
        for requirement in self.install_requires:
            requirementsStr += '\n        %r,' % requirement
        data['install_requires'] = requirementsStr

        data['extras_require'] = pprint.pformat(
            self.extras_requires, width=1)

        data['entry_points'] = pprint.pformat(
            self.entry_points, width=1)

        data['classifiers'] = pprint.pformat(
            self.classifiers, width=1)

        return template % data

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.getProject().name)
