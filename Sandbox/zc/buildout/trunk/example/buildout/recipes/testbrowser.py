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
import buildout


class Default(buildout.DownloadSource):

    name = 'testbrowser'
    version = buildout.getVersion(name)
    download_url = ('svn://svn.zope.org/repos/main/Zope3/' + version +
                    '/src/zope/testbrowser')

    def build(self):
        pass
    
    def install(self):
        buildout.linkOrCopy('../../../../var/src/testbrowser/',
                            'instance/lib/python/zope/testbrowser')
