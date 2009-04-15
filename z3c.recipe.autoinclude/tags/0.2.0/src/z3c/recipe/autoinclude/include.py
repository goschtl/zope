##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""z3c autoinclude recipe

$Id$
"""
import os
import zc.buildout
import zc.recipe.egg
import pkg_resources
from dependency import DependencyFinder


class AutoIncludeSetup(object):

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name
        self.options = options
        self.location = options.get('location', 'packages.zcml')
        self.egg = zc.recipe.egg.Eggs(buildout, name, options)

    def install(self):
        eggs, ws = self.egg.working_set()

        dists = [ws.find(pkg_resources.Requirement.parse(spec)) for spec in eggs]

        meta = []
        configure = []
        overrides = []
        exclude = []

        for dist in dists:
            info = DependencyFinder(dist, ws).includableInfo(
                ['meta.zcml', 'configure.zcml', 'overrides.zcml', 'exclude.zcml'])

            for pkg in info['meta.zcml']:
                if pkg not in meta:
                    meta.append(pkg)

            for pkg in info['configure.zcml']:
                if pkg not in configure:
                    configure.append(pkg)

            for pkg in info['overrides.zcml']:
                if pkg not in overrides:
                    overrides.append(pkg)

            for pkg in info['exclude.zcml']:
                if pkg not in exclude:
                    exclude.append(pkg)

        meta = ''.join(
            ['<include package="%s" file="meta.zcml" />\n'%pkg for pkg in meta])

        overrides = ''.join(
            ['<includeOverrides package="%s" file="overrides.zcml" />\n'%pkg 
             for pkg in overrides])

        exclude = ''.join(
            ['<include package="%s" file="exclude.zcml" />\n'%pkg for pkg in exclude])

        configureData = ''.join(
            ['<include package="%s" />\n'%pkg for pkg in configure])

        # fix zope.app.xxx dependencies problem
        if 'zope.app.appsetup' in configure:
            configureData = (
                '<include package="zope.app.appsetup" />\n' +
                configureData)

        if 'zope.app.zcmlfiles' in configure:
            configureData = (
                '<include package="zope.app.zcmlfiles" file="menus.zcml" />\n' +
                configureData)

        dest = []

        location = self.location

        if location and not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        open(os.path.join(location, 'packages-meta.zcml'), 'w').write(
            packages_zcml_template % meta)

        open(os.path.join(location, 'packages-configure.zcml'), 'w').write(
            packages_zcml_template % configureData)

        open(os.path.join(location, 'packages-overrides.zcml'), 'w').write(
            packages_zcml_template % overrides)

        open(os.path.join(location, 'packages-exclude.zcml'), 'w').write(
            packages_zcml_template % exclude)

        return dest

    update = install


packages_zcml_template = """\
<configure xmlns="http://namespaces.zope.org/zope">

%s
</configure>
"""
