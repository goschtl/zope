#! /usr/bin/env python2.2
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
"""

$Id: z3.py,v 1.6 2002/11/18 20:20:11 jim Exp $
"""

import os, sys, asyncore

basepath = filter(None, sys.path)

def run(argv=sys.argv):

    # Refuse to run without principals.zcml
    if not os.path.exists('principals.zcml'):
        print """ERROR: You need to create principals.zcml

        The file principals.zcml contains your "bootstrap" user
        database. You aren't going to get very far without it.  Start
        by copying principals.zcml.in and then look at
        sample_principals.zcml for some example principal and role
        settings."""
        sys.exit(1)

    # setting python paths
    program = argv[0]
    here = os.path.join(os.getcwd(), os.path.split(program)[0])
    libpython = os.path.join(here,'lib','python') 
    sys.path=[libpython, here] + basepath

    # temp hack
    dir = os.getcwd()

    # Do global software config
    from Zope.App import config
    config('site.zcml')
    
    # Load server config
    if (not os.path.exists('zserver.zcml')
        and os.path.exists('zserver.zcml.in')
        ):
        open('zserver.zcml', 'w').write(open('zserver.zcml.in').read())
        
    from Zope.Configuration.xmlconfig import XMLConfig
    XMLConfig(os.path.join(dir, 'zserver.zcml'))()

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        # Exit without spewing an exception.
        pass
    sys.exit(0)


if __name__ == '__main__':
    run()
    
