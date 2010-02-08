##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Debug recipes for Zope3 apps

$Id$
"""

import os
import zc.buildout
import zc.recipe.egg

import code
import zope.app.wsgi
import zope.app.debug

class DebugSetup:
    """Paste serve setup script."""

    def __init__(self, buildout, name, options):
        self.app = None
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        if options.get('app') is None:
            raise zc.buildout.UserError(
                'You have to define at the app (which has the eggs and zope.conf).')
        self.app = options.get('app')
        options['eggs'] = '%s\nz3c.recipe.paster' % buildout[self.app]['eggs']

        if not options.get('working-directory', ''):
            options['location'] = buildout[self.app].get('location',
                os.path.join(buildout['buildout']['parts-directory'], self.app))

        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options
        location = options['location']
        executable = self.buildout['buildout']['executable']

        # setup path
        installed = []
        if not os.path.exists(location):
            os.mkdir(location)
            installed.append(location)

        zope_conf_path = os.path.join(location, 'zope.conf')

        # setup paster script
        if self.egg is not None:
            extra_paths = self.egg.extra_paths
        else:
            extra_paths = []

        eggs, ws = self.egg.working_set()

        installed.extend(zc.buildout.easy_install.scripts(
            [(self.name, 'z3c.recipe.paster.debug', 'main')],
            ws, self.options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = "%r" % zope_conf_path,
            ))

        return installed

    update = install


def main(zope_conf):
    db = zope.app.wsgi.config(zope_conf)
    debugger = zope.app.debug.Debugger.fromDatabase(db)
    # Invoke an interactive interpreter shell
    banner = ("Welcome to the interactive debug prompt.\n"
              "The 'root' variable contains the ZODB root folder.\n"
              "The 'app' variable contains the Debugger, 'app.publish(path)' "
              "simulates a request.")
    code.interact(banner=banner, local={'debugger': debugger,
                                        'app':      debugger,
                                        'root':     debugger.root()})