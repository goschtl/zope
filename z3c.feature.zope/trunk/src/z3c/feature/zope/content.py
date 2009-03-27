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
"""Zope Content-type feature.

$Id$
"""
import os
import zope.interface
from zope.schema.fieldproperty import FieldProperty

from z3c.builder.core import project, zcml, python, form
from z3c.feature.core import base, xml
from z3c.feature.zope import interfaces

CONTENT_DOCUMENTATION = """
The Zope Content Feature lets you define a basic content type that can
be stored in a database and that has a simple page for creating,
reading, updating, and deleting the content item.
"""

class ZopeContentFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IZopeContentFeature)

    featureDocumentation = CONTENT_DOCUMENTATION
    featureSingleton = False
    featureDependencies = ('zope-project','zope-skin')

    className = FieldProperty(interfaces.IZopeContentFeature['className'])
    classFile = FieldProperty(interfaces.IZopeContentFeature['classFile'])
    fields = FieldProperty(interfaces.IZopeContentFeature['fields'])


    @property
    def featureTitle(self):
        return u'Zope Content Type (%s)' % self.className

    def __init__(self):
        self.fields = {}

    def addField(self, name, schemaType):
        constraint = interfaces.IZopeContentFeature['fields']
        constraint.key_type.validate(name)
        constraint.value_type.validate(schemaType)
        self.fields[name] = schemaType

    def update(self, features=()):
        if not self.classFile:
            self.classFile = self.className.lower()+'.py'

    @classmethod
    def fromXMLNode(cls, node, omit=()):
        feature = cls()
        schema = base.getFeatureSchema(feature)
        for fieldName in ('className','classFile'):
            matches = node.xpath('./%s'%fieldName)
            match = matches[0] if matches else None
            if match is not None:
                setattr(feature, fieldName, unicode(match.text))
        for field in node.xpath('./fields/field'):
            feature.addField(unicode(field.get('name')),
                             unicode(field.get('type')))
        return feature

    def _applyTo(self, project):
        # Step 1: build the interface
        ifaces = project.package['interfaces.py']

        iface = python.InterfaceBuilder(u'I%s' % self.className)
        iface.docstring = str("The ``%s`` Content Type" % self.className)
        ifaces.add(iface)

        for fieldName, fieldType in self.fields.items():
            iface.add(python.FieldBuilder(
                name=fieldName,
                type=str(fieldType),
                title=fieldName.capitalize()))

        # Step 2: build the implementation
        if self.classFile not in project.package.keys():
            project.package.add(python.ModuleBuilder(self.classFile))
        module = project.package[self.classFile]

        classDefinition = python.ClassFromInterfaceBuilder(
            name=self.className,
            interface=iface,
            bases = ('persistent.Persistent',
                     'zope.container.contained.Contained'))
        module.add(classDefinition)

        # Step 3: build the configuration
        if 'configure' not in project.package.keys():
            project.package.add(zcml.ZCMLFileBuilder(u'configure.zcml'))
        configure = project.package['configure']

        classDirective = zcml.ZCMLDirectiveBuilder(
            namespace=zcml.ZOPE_NS,
            name='class',
            attributes={'class':classDefinition.getPythonPath()})
        configure.add(classDirective)

        classDirective.add(zcml.ZCMLDirectiveBuilder(
            namespace=None,
            name='allow',
            attributes={'interface':iface.getPythonPath()}))
        classDirective.add(zcml.ZCMLDirectiveBuilder(
            namespace=None,
            name='require',
            attributes={'permission':'zope.Public',
                        'set_schema':iface.getPythonPath()}))

        browser = project.package['browser']

        # Step 4: make sure the browser package has configuration in it.
        if 'configure' not in browser.keys():
            browser.add(zcml.ZCMLFileBuilder(u'configure.zcml'))
            configure.add(zcml.ZCMLDirectiveBuilder(
                namespace = zcml.ZOPE_NS,
                name = 'include',
                attributes={'package':browser.getPythonPath()}))
        browserConfig = browser['configure']

        # Step 5: create the form module.
        if 'z3c.form' not in project.setup.install_requires:
            project.setup.install_requires.append('z3c.form')
        project.package['appConfig'].add(
            zcml.ZCMLDirectiveBuilder(
                namespace = zcml.ZOPE_NS,
                name = 'include',
                attributes={'package':'z3c.form','file':'meta.zcml'})
            )
        project.package['appConfig'].add(
            zcml.ZCMLDirectiveBuilder(
                namespace = zcml.ZOPE_NS,
                name = 'include',
                attributes={'package':'z3c.form'})
            )
        layerIface = project.package['interfaces.py']['ILayer']
        skinIface = project.package['interfaces.py']['ISkin']
        if 'z3c.form.interfaces.IFormLayer' not in skinIface.bases:
            skinIface.bases.append('z3c.form.interfaces.IFormLayer')

        formModule = python.ModuleBuilder(self.classFile)
        browser.add(formModule)

        # Step 5.1: create the add form and register it
        addForm = form.AddFormBuilder(
            name=u'%sAddForm' % self.className,
            #TODO: make add form builder accept an interface builder.
            interface=str(iface.getPythonPath()),
            fields=iface.keys(),
            factory=str(classDefinition.getPythonPath()),
            next='index.html')
        formModule.add(addForm)
        browserConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace=zcml.BROWSER_NS,
            name=u'page',
            attributes = {
                'name': 'index.html',
                'for': 'zope.app.folder.interfaces.IFolder',
                #TODO: make add forms support a getPythonPath method...
                'class': '%s.%s'%(formModule.getPythonPath(),
                                  addForm.name),
                'permission': 'zope.Public',
                'layer':layerIface.getPythonPath()}))


        # Step 5.2 create the edit form and register it.
        editForm = form.EditFormBuilder(
            name=u'%sEditForm' % self.className,
            interface=str(iface.getPythonPath()),
            fields=iface.keys())
        formModule.add(editForm)
        browserConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace=zcml.BROWSER_NS,
            name=u'page',
            attributes = {
                'name': 'edit.html',
                'for': str(iface.getPythonPath()),
                #TODO: make add forms support a getPythonPath method...
                'class': '%s.%s'%(formModule.getPythonPath(),
                                    editForm.name),
                'permission': 'zope.Public',
                'layer':layerIface.getPythonPath()}))

        # Step 5.3 create the display form and register it.
        displayForm = form.SimpleDisplayFormBuilder(
            name=u'%sDisplayForm' % self.className,
            interface=str(iface.getPythonPath()),
            fields=iface.keys())
        formModule.add(displayForm)
        browserConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace=zcml.BROWSER_NS,
            name=u'page',
            attributes = {
                'name': 'index.html',
                'for': str(iface.getPythonPath()),
                #TODO: make add forms support a getPythonPath method...
                'class': '%s.%s'%(formModule.getPythonPath(),
                                    displayForm.name),
                'permission': 'zope.Public',
                'layer':layerIface.getPythonPath()}))
