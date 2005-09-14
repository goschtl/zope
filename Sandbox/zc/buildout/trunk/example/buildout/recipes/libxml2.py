##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os, sys
import buildout


class Default(buildout.DownloadSource):
    def __init__(self):
        self.name = 'libxml2'
        version = buildout.getVersion(self.name)
        self.download_url = \
            'http://xmlsoft.org/sources/libxml2-sources-%s.tar.gz' % version
        self.unarchived_name='libxml2-%s' % version
        self.prefix = buildout.getBuildPath(self.name)
        self.site_packages = os.path.join(self.prefix, 'lib', 'python')

    def build(self):
        cache_file = os.path.abspath(
                buildout.queryOption('configure', 'cache_file'))

        def helper():
            os.chdir(buildout.getSourcePath(self.name))
            buildout.runCommand('./configure', [
                    '--prefix='+self.prefix,
                    '--cache-file='+cache_file,
                    '--with-python='+buildout.getBuildPath('python'),
                   ])
            buildout.runCommand('make PYTHON_SITE_PACKAGES='
                                + self.site_packages)
            buildout.runCommand('make PYTHON_SITE_PACKAGES='
                                + self.site_packages + ' install')

        buildout.dirBuildHelper(self.prefix, helper)

    def install(self): 
        buildout.registerPythonPackage(self.site_packages)

    def freshen(self):
        pass


class Windows(buildout.DownloadFile, buildout.WindowsInstaller):
    def __init__(self):
        self.name = 'libxml2'
        version = buildout.getVersion(self.name)
        self.download_url = (
            'http://users.skynet.be/sbi/libxml-python/binaries/'
            'libxml2-python-%s.win32-py%s.exe' 
            % (version, self.short_python_version))
        self.install_marker = os.path.join(buildout.getBuildPath('python'), 
                'Lib', 'site-packages', 'libxml2.py')
