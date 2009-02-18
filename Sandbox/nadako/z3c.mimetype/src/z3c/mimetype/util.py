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
'''
$Id$
'''
import os

XDG_DATA_HOME = os.environ.get('XDG_DATA_HOME', os.path.join(os.environ.get('HOME', '/'), '.local', 'share'))
XDG_DATA_DIRS = [XDG_DATA_HOME] + [dir for dir in os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if dir]

def iterDataPaths(*resource):
    resource = os.path.join(*resource)
    for data_dir in XDG_DATA_DIRS:
        path = os.path.join(data_dir, resource)
        if os.path.exists(path):
            yield path
