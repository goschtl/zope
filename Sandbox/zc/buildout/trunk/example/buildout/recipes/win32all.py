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
import os
import buildout

class Windows(buildout.DownloadFile, buildout.WindowsInstaller):
    def __init__(self):
        self.name = 'win32all'
        version = buildout.getVersion(self.name)
        self.download_url = (
            'http://easynews.dl.sourceforge.net/sourceforge/pywin32/'
            'pywin32-%s.win32-py%s.exe'
            % (version, self.short_python_version))
        self.install_marker = os.path.join(buildout.getBuildPath('python'), 
                'Lib', 'site-packages', 'libxml2.py')
