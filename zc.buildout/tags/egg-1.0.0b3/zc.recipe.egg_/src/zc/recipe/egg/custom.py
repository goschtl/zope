##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Install packages as eggs

$Id$
"""

import os, re, zipfile
import zc.buildout.easy_install

class Base:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        options['_d'] = buildout['buildout']['develop-eggs-directory']

        python = options.get('python', buildout['buildout']['python'])
        options['executable'] = buildout[python]['executable']

        self.build_ext = build_ext(buildout, options)


    def update(self):
        return self.install()

class Custom(Base):

    def __init__(self, buildout, name, options):
        Base.__init__(self, buildout, name, options)

        links = options.get('find-links',
                            buildout['buildout'].get('find-links'))
        if links:
            links = links.split()
            options['find-links'] = '\n'.join(links)
        else:
            links = ()
        self.links = links

        index = options.get('index', buildout['buildout'].get('index'))
        if index is not None:
            options['index'] = index
        self.index = index

        options['_e'] = buildout['buildout']['eggs-directory']

        assert options.get('unzip') in ('true', 'false', None)

        if buildout['buildout'].get('offline') == 'true':
            self.install = lambda: ()

    def install(self):
        options = self.options
        distribution = options.get('eggs', self.name).strip()
        return zc.buildout.easy_install.build(
            distribution, options['_d'], self.build_ext,
            self.links, self.index, options['executable'], [options['_e']],
            )
        
class Develop(Base):

    def __init__(self, buildout, name, options):
        Base.__init__(self, buildout, name, options)
        options['setup'] = os.path.join(buildout['buildout']['directory'],
                                        options['setup'])

    def install(self):
        options = self.options
        return zc.buildout.easy_install.develop(
            options['setup'], options['_d'], self.build_ext,
            options['executable'],
            )
        

def build_ext(buildout, options):
    result = {}
    for be_option in ('include-dirs', 'library-dirs', 'rpath'):
        value = options.get(be_option)
        if value is None:
            continue
        value = [
            os.path.join(
                buildout['buildout']['directory'],
                v.strip()
                )
            for v in value.strip().split('\n')
            if v.strip()
        ]
        result[be_option] = os.pathsep.join(value)
        options[be_option] = os.pathsep.join(value)

    swig = options.get('swig')
    if swig:
        options['swig'] = result['swig'] = os.path.join(
            buildout['buildout']['directory'],
            swig,
            )

    for be_option in ('define', 'undef', 'libraries', 'link-objects',
                      'debug', 'force', 'compiler', 'swig-cpp', 'swig-opts',
                      ):
        value = options.get(be_option)
        if value is None:
            continue
        result[be_option] = value

    return result
