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
"""Buildout Configuration Builder

$Id$
"""
import os
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.builder.core import base, interfaces

class PartBuilder(base.ContentBuilder):
    zope.interface.implements(interfaces.IPartBuilder)

    values = FieldProperty(interfaces.IPartBuilder['values'])
    autoBuild = FieldProperty(interfaces.IPartBuilder['autoBuild'])

    def __init__(self, name, values=None, autoBuild=True):
        super(PartBuilder, self).__init__(name)
        if values is None:
            values = []
        self.values = list(values)
        self.autoBuild = autoBuild

    def addValue(self, key, value):
        self.values.append((key, value))

    def removeValue(self, key):
        for item in self.values:
            if item[0] == key:
                self.values.remove(item)
                return

    def render(self):
        output = ''
        output += '[%s]\n' %self.name
        for key, value in self.values:
            output += '%s = %s\n' %(key, value)
        return output


class BuildoutConfigBuilder(base.BuilderContainer, base.FileBuilder):
    zope.interface.implements(interfaces.IBuildoutConfigBuilder)

    extends = FieldProperty(interfaces.IBuildoutConfigBuilder['extends'])
    names = FieldProperty(interfaces.IBuildoutConfigBuilder['names'])

    def __init__(self):
        super(BuildoutConfigBuilder, self).__init__(u'buildout.cfg')
        self.extends = [u'http://download.zope.org/zope3.4/3.4.0/versions.cfg']
        self.names = []

    def update(self):
        self.names = [part.name for part in self.values()
                      if part.autoBuild]
        for part in self.values():
            part.update()

    def render(self):
        output = ''
        output += '[buildout]\n'
        output += 'extends = %s\n' %('   \n'.join(self.extends))
        output += 'develop = .\n'
        output += 'parts = %s\n' %' '.join(self.names)
        output += 'versions = versions\n'
        if len(self):
            output += '\n'
        for part in self.values():
            output += part.render()
            output += '\n'
        return output

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.getProject().name)
