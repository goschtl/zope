##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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

import sys, errno, os.path

def addPackagePaths(INSTANCE_HOME=''):
    if INSTANCE_HOME:
        buildout_root = os.path.dirname(INSTANCE_HOME)
    else:
        buildout_root = ''

    try:
        in_file = open(os.path.join(buildout_root, 'var/opt/paths'))
    except IOError, e:
        if e.errno != errno.ENOENT:
            raise
    else:
        paths = [l.strip() for l in in_file.readlines()]
        in_file.close()
        sys.path[:0] = paths
