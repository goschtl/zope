##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
if not sys.modules.has_key('Testing'):
    p0 = sys.path[0]
    if p0 and __name__ == '__main__':
        os.chdir(p0)
        p0 = ''
    p = d = os.path.abspath(os.curdir)
    while d:
        if os.path.isdir(os.path.join(p, 'Testing')):
            sys.path[:1] = [p0, os.pardir, p]
            break
        p, d = os.path.split(p)
    else:
        print 'Unable to locate Testing package.'
        sys.exit(1)

import Testing, unittest
execfile(os.path.join(os.path.split(Testing.__file__)[0], 'common.py'))


