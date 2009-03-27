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
"""Representation of ZCML Configuration files.

$Id$
"""
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from z3c.builder.core import base, interfaces

ZOPE_NS = 'http://namespaces.zope.org/zope'
BROWSER_NS = 'http://namespaces.zope.org/browser'
ZCML_NS = 'http://namespaces.zope.org/zcml'
Z3C_NS = 'http://namespaces.zope.org/z3c'


class ZCMLDirectiveBuilder(base.BuilderContainer, base.ContentBuilder):
    zope.interface.implements(interfaces.IZCMLDirectiveBuilder)

    namespace = FieldProperty(interfaces.IZCMLDirectiveBuilder['namespace'])
    #name = FieldProperty(interfaces.IZCMLDirectiveBuilder['name'])
    attributes = FieldProperty(interfaces.IZCMLDirectiveBuilder['attributes'])
    indent = FieldProperty(interfaces.IZCMLDirectiveBuilder['indent'])

    _indentSpaces = 2
    _indentAttributeSpaces = 4

    def __init__(self, namespace, name, attributes=None, indent=0):
        super(ZCMLDirectiveBuilder, self).__init__(unicode(name))
        self.namespace = namespace
        if not attributes:
            attributes = {}
        self.attributes = attributes
        self.indent = indent

    def getZCMLBuilder(self):
        """See interfaces.IZCMLDirectiveBuilder"""
        builder = self
        while not interfaces.IZCMLFileBuilder.providedBy(builder):
            builder = builder.__parent__
        return builder

    def add(self, builder):
        """See interfaces.IBuilderContainer"""
        name = base.getUUID()
        self[name] = builder
        return name

    def update(self):
        """See interfaces.IBaseBuilder"""
        zcml = self.getZCMLBuilder()
        if self.namespace is not None and self.namespace not in zcml.namespaces:
            zcml.namespaces.append(self.namespace)
        for builder in self.values():
            builder.indent = self.indent + 1
            builder.update()

    def render(self):
        """See interfaces.IContentBuilder"""
        output = ''
        prefix = ''
        if self.namespace:
            prefix = self.namespace.rsplit('/')[-1] + ':'
        # Write XML node
        indent = ' ' * self._indentSpaces * self.indent
        attrIndent = indent + ' '*self._indentAttributeSpaces
        output += indent + '<%s%s' %(prefix, self.name)
        if self.attributes:
            for name, attr in reversed(self.attributes.items()):
                output += '\n' + attrIndent + '%s="%s"' %(name, attr)
            output += '\n' + attrIndent
        if not len(self):
            output += '/>\n'
            return output
        output += '>\n'
        # Write all sub-builders.
        for builder in self.values():
            output += builder.render()
            output += '\n'
        # Close XML node.
        output += indent + '</%s%s>\n' %(prefix, self.name)
        # Return result.
        return output


class ZCMLFileBuilder(ZCMLDirectiveBuilder, base.FileBuilder):
    zope.interface.implements(interfaces.IZCMLFileBuilder)

    i18n_domain = FieldProperty(interfaces.IZCMLFileBuilder['i18n_domain'])
    namespaces = FieldProperty(interfaces.IZCMLFileBuilder['namespaces'])

    def __init__(self, name):
        ZCMLDirectiveBuilder.__init__(self, None, 'configure')
        base.FileBuilder.__init__(self, self.name, str(name))

    def update(self):
        """See interfaces.IBaseBuilder"""
        self.namespaces = []
        if not self.i18n_domain:
            project = self.getProject()
            self.i18n_domain = project.name
        super(ZCMLFileBuilder, self).update()
        # Create list of attributes
        self.attributes = {}
        if self.i18n_domain:
            self.attributes['i18n_domain'] = self.i18n_domain
        for namespace in self.namespaces:
            name = namespace.rsplit('/', 1)[-1]
            self.attributes['xmlns:'+name] = namespace

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.filename)
