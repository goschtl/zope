##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
import os.path
from os.path import join, dirname
import logging

import shutil
import zc.buildout
import zc.recipe.egg
import zc.buildout.easy_install
import pkg_resources

confPyTemplate = """
templates_path = ['%(templatesDir)s']
source_suffix = '.txt'
master_doc = '%(indexDoc)s'
project = '%(project)s'
copyright = '%(copyright)s'
version = '%(version)s'
release = '%(release)s'
today_fmt = '%%B %%d, %%Y'
pygments_style = 'sphinx'
html_style = 'default.css'
html_static_path = ['%(staticDir)s']
html_last_updated_fmt = '%%b %%d, %%Y'
"""

arg_template = """[
  '-c', '%(CONFPATH)s',
  '%(SRCPATH)s',
  '%(BUILDPATH)s',
  ]"""

class ZopeOrgSetup(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = join(buildout['buildout']['bin-directory'],
                                 options.get('script', self.name))
        self.egg = zc.recipe.egg.Egg(self.buildout, self.name, self.options)

    def install(self):
        installed = []
        eggs, workingSet = self.egg.working_set()
        docs = [workingSet.find(pkg_resources.Requirement.parse(spec))
                for spec in eggs]

        # Create parts directory for configuration files.
        installDir = join(self.buildout['buildout']['parts-directory'], self.name)
        if not os.path.isdir(installDir):
            os.mkdir(installDir)

        #for each egg listed as a buildout option, create a configuration space.
        for doc in docs:
            partDir = join(installDir, doc.project_name)
            if not os.path.isdir(partDir):
                os.mkdir(partDir)
            installed.append(partDir)

            recipeDir = dirname(__file__)

            #create static directory
            staticDir = join(partDir, '.static')
            if not os.path.isdir(staticDir):
                os.mkdir(staticDir)
            installed.append(staticDir)
            shutil.copy(join(recipeDir,'default.css'),
                        join(staticDir, 'default.css'))
            installed.append(join(staticDir, 'default.css'))

            #create tempaltes directory
            templatesDir = join(partDir, '.templates')
            if not os.path.isdir(templatesDir):
                os.mkdir(templatesDir)
            installed.append(templatesDir)
            shutil.copy(join(recipeDir,'layout.html'),
                        join(templatesDir, 'layout.html'))
            installed.append(join(templatesDir, 'layout.html'))


            #create conf.py
            confPyPath = join(partDir, 'conf.py')
            confPy = open(confPyPath, 'w')
            confPy.write(confPyTemplate % dict(project=doc.project_name,
                                               copyright='some copyright',
                                               version=doc._version,
                                               release=doc._version,
                                               staticDir=staticDir,
                                               templatesDir=templatesDir,
                                               indexDoc=self.options.get('indexDoc','index')
                                               ))
            confPy.close()
            installed.append(confPyPath)

            buildDir = self.options.get('build-dir',
                                        os.path.join(partDir, 'build'))
            if not os.path.isdir(buildDir):
                os.mkdir(buildDir)

            defaults = self.options.get('defaults', '').strip()
            if defaults:
                defaults = '(%s) + ' % defaults

            args = arg_template % dict(CONFPATH=partDir,
                                       SRCPATH=".",
                                       BUILDPATH=buildDir)
            installed.extend(zc.buildout.easy_install.scripts(
                [(self.options['script'],
                  'sphinx',
                  'main')],
                workingSet,
                self.options['executable'],
                self.buildout['buildout']['bin-directory'],
                extra_paths=self.egg.extra_paths,
                ## arguments = defaults + args,
                initialization = "import sys; sys.argv.extend(%s)" % args,
                ))

        return installed

    update = install
