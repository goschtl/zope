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
        self.name = 'zope3'
        version = buildout.getVersion(self.name)
        self.download_url = 'svn://svn.zope.org/repos/main/Zope3/' + version

    def build(self):
        source_path = buildout.getSourcePath('zope3')
        buildout.chdir(source_path)
        try:
            buildout.runCommand(
                    'make', ('PYTHON='+buildout.getPathToBinary('python'),))
        finally:
            buildout.popdir()

    def install(self): 
        pass


class Windows(buildout.DownloadSource):
    def __init__(self):
        self.name = 'zope3'
        version = buildout.getVersion(self.name)
        self.download_url = 'svn://svn.zope.org/repos/main/Zope3/' + version
        self.pyd_recipe = PydRecipe()

    def get(self):
        self.pyd_recipe.get()
        super(Windows, self).get()

    def build(self):
        pass

    def install(self):
        self.pyd_recipe.install()


# this is used by the Windows recipe to get the dlls
class PydRecipe(buildout.DownloadFile):
    def __init__(self):
        # XXX we always download the libraries associated with the head, we
        # will have to do something else when we need to use a release
        self.download_url = \
            'http://www.zope.org/Members/tim_one/Zope3-Py2.4-pyd.zip'

    def install(self):
        zip = buildout.fileFromUrl(self.download_url)
        zip_path = os.path.join(buildout.getBaseArchivePath(), zip)
        buildout.extract(zip_path, dir=buildout.getSourcePath('zope3'))
