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
#!/usr/bin/env python2.4
import sys, os

ENGINE_PATH = './buildout/engine'
ENGINE_URL = 'svn://svn.zope.org/repos/main/Sandbox/zc/buildout'

# bootstrap the buildout code, if it doesn't yet exist
if os.path.exists(ENGINE_PATH):
    os.system('svn up %s' % ENGINE_PATH)
else:
    os.system('svn co %s %s ' % (ENGINE_URL, ENGINE_PATH))

sys.path.append(os.path.abspath(ENGINE_PATH))
sys.path.append(os.path.abspath('./buildout'))
from buildout import main
main(sys.argv)
