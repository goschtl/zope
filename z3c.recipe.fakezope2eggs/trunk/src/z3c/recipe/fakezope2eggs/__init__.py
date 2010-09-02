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
import os

EGG_INFO_CONTENT = """Metadata-Version: 1.0
Name: %s
Version: 0.0
"""


class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        options.setdefault('zope2-part', 'zope2')
        options.setdefault('zope2-location', '')
        options.setdefault('additional-fake-eggs', '')
        options.setdefault('skip-fake-eggs', '')

    def install(self):
        zope2Location = self.options['zope2-location'].strip()
        if zope2Location == '':
            zope2Part = self.options['zope2-part'].strip()
            zope2Location = self.buildout[zope2Part]['location']

        developEggDir = self.buildout['buildout']['develop-eggs-directory']
        zopeLibZopeLocation = os.path.join(zope2Location, 'lib', 'python',
                                           'zope')
        zopeLibZopeAppLocation = os.path.join(zope2Location, 'lib', 'python',
                                              'zope', 'app')
        zopeLibs = ["zope.%s" % lib for lib in os.listdir(zopeLibZopeLocation)\
                    if os.path.isdir(os.path.join(zopeLibZopeLocation, lib))]
        zopeLibs += ["zope.app.%s" % lib for lib in os.listdir(zopeLibZopeAppLocation)\
                    if os.path.isdir(os.path.join(zopeLibZopeAppLocation, lib))]
        zopeLibs += [lib for lib in self.options['additional-fake-eggs'].split('\n')]
        zopeLibs = [lib for lib in zopeLibs if lib not in
                    self.options.get('skip-fake-eggs', '').split('\n')]
        for zopeLib in zopeLibs:
            fakeLibEggInfoFile = os.path.join(developEggDir,
                                              '%s.egg-info' % zopeLib)
            fd = open(fakeLibEggInfoFile, 'w')
            fd.write(EGG_INFO_CONTENT % zopeLib)
            fd.close()
        return ()

    def update(self):
        return self.install()
