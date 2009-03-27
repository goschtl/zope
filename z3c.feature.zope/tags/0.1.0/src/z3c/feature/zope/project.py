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
"""Zope Project Feature

$Id$
"""
import zope.interface
from z3c.builder.core import buildout, python, zcml
from z3c.feature.core import base
from z3c.feature.zope import interfaces

PROJECT_DOCUMENTATION = u'''
This feature extends a buildout project to a Zope project.
'''

class ZopeProjectFeature(base.BaseFeature):
    zope.interface.implements(interfaces.IZopeProjectFeature)

    featureTitle = u'Zope Project'
    featureDocumentation = PROJECT_DOCUMENTATION

    def _applyTo(self, project):
        # Create application ZCML.
        appConfig = zcml.ZCMLFileBuilder(u'application.zcml')
        project.package['appConfig'] = appConfig

        for name in ('zope.app.component',
                     'zope.app.component.browser',
                     'zope.app.pagetemplate',
                     'zope.app.publication',
                     'zope.app.publisher',
                     'zope.app.security',
                     'zope.app.securitypolicy',
                     'zc.configuration',
                     'z3c.form',
                     'z3c.template',
                     'z3c.pagelet',
                     'z3c.macro',
                     'zope.viewlet',
                     ):
            id = appConfig.add(zcml.ZCMLDirectiveBuilder(
                namespace = zcml.ZOPE_NS,
                name = 'include',
                attributes = {
                    'package': name,
                    'file': 'meta.zcml'}
                ))

        for package, filename in (
            ('zope.app.securitypolicy.browser', 'configure.zcml'),
            ('zope.app.session', 'browser.zcml'),
            ('zope.app.folder.browser', 'configure.zcml'),
            ):
            id = appConfig.add(zcml.ZCMLDirectiveBuilder(
                namespace = zcml.ZOPE_NS,
                name = 'exclude',
                attributes = {'package': package, 'file': filename}
                ))

        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.BROWSER_NS,
            name = 'menu',
            attributes = {
                'id': 'zmi_views',
                'title': 'Views'}
            ))

        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.BROWSER_NS,
            name = 'menu',
            attributes = {
                'id': 'zmi_actions',
                'title': 'Actions'}
            ))

        for name in ('zope.app.appsetup',
                     'zope.app.component',
                     'zope.app.container',
                     'zope.app.error',
                     'zope.app.i18n',
                     'zope.app.publication',
                     'zope.app.security',
                     'zope.app.securitypolicy',
                     'zope.app.session',
                     'zope.app.twisted',
                     'zope.app.wsgi',
                     'zope.annotation',
                     'zope.component',
                     'zope.container',
                     'zope.location',
                     'zope.publisher',
                     'zope.traversing',
                     'zope.traversing.browser',
                     'zope.app.folder',
                     'z3c.macro',
                     'z3c.form',
                     'z3c.formui',
                     'z3c.pagelet',
                     'z3c.layer.pagelet',
                     ):
            id = appConfig.add(zcml.ZCMLDirectiveBuilder(
                namespace = zcml.ZOPE_NS,
                name = 'include',
                attributes = {'package': name}
                ))

        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.ZOPE_NS,
            name = 'include',
            attributes = {'package': project.name}
            ))

        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.BROWSER_NS,
            name = 'defaultView',
            attributes = {
                'name': 'index.html'}
            ))
        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.ZOPE_NS,
            name = 'securityPolicy',
            attributes = {
                'component': 'zope.securitypolicy.zopepolicy.ZopeSecurityPolicy'}
            ))
        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.ZOPE_NS,
            name = 'role',
            attributes = {
                'id': 'zope.Anonymous',
                'title': 'Everybody'}
            ))
        appConfig.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.ZOPE_NS,
            name = 'grantAll',
            attributes = {
                'role': 'zope.Anonymous'}
            ))

        # Create `browser` package.
        project.package.add(python.PackageBuilder(u'browser'))
        project.package['browser'].add(zcml.ZCMLFileBuilder(u'configure.zcml'))

        # Create package configuration file.
        config = zcml.ZCMLFileBuilder(u'configure.zcml')
        config.add(zcml.ZCMLDirectiveBuilder(
            namespace = zcml.ZOPE_NS,
            name = 'include',
            attributes = {
                'package': '.browser'}
            ))
        project.package.add(config)

        if 'versions' not in project.buildout.keys():
            project.buildout.add(buildout.PartBuilder(
                u'versions',
                autoBuild=False
                ))
        for version in (('zc.configuration','1.0'),
                        ('z3c.layer.pagelet','1.0.1')):
            project.buildout['versions'].addValue(*version)

        # Create buildout parts.
        project.buildout.add(buildout.PartBuilder(
            u'zope3',
            [('location', '.')],
            autoBuild=False
            ))
        project.buildout.add(buildout.PartBuilder(
            u'%s-app' %project.name,
            [('recipe', 'zc.zope3recipes:app'),
             ('site.zcml',
              '<include package="%s" file="application.zcml" />' %project.name),
             ('eggs', project.name)]
            ))
        project.buildout.add(buildout.PartBuilder(
            project.name,
            [('recipe', 'zc.zope3recipes:instance'),
             ('application', '%s-app' %project.name),
             ('zope.conf', '${database:zconfig}'),
             ('eggs', project.name)]
            ))
        project.buildout.add(buildout.PartBuilder(
            u'database',
            [('recipe', 'zc.recipe.filestorage')],
            autoBuild=False
            ))

        # Add dependencies.
        project.setup.install_requires += [
            'zdaemon',
            'zc.configuration',
            'zc.zope3recipes',
            'zope.app.securitypolicy',
            'zope.app.container',
            'zope.app.session',
            'zope.app.twisted',
            'zope.container',
            'z3c.formui',
            'z3c.pagelet',
            'z3c.layer.pagelet',
            ]
