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
"""Start script for Zope3: loads configuration and starts the server.

$Id: z3.py,v 1.13 2002/12/25 19:28:50 tim_one Exp $
"""

import os, sys

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
    srcdir = os.path.abspath('src')
    sys.path = [srcdir, here] + basepath

    # Initialize the logging module.
    import logging.config
    logging.basicConfig()
    logging.root.setLevel(logging.CRITICAL)
    # If log.ini exists, use it
    if os.path.exists("log.ini"):
        logging.config.fileConfig("log.ini")

    # temp hack
    dir = os.getcwd()

    # Copy products.zcml.in, if necessary
    if (not os.path.exists('products.zcml')
        and os.path.exists('products.zcml.in')
        ):
        open('products.zcml', 'w').write(open('products.zcml.in').read())

    # Do global software config
    from zope.app import config
    config('site.zcml')

    # Load server config
    if (not os.path.exists('zserver.zcml')
        and os.path.exists('zserver.zcml.in')
        ):
        open('zserver.zcml', 'w').write(open('zserver.zcml.in').read())

    from zope.configuration.xmlconfig import XMLConfig
    XMLConfig(os.path.join(dir, 'zserver.zcml'))()

    from zodb.zeo import threadedasync
    try:
        threadedasync.loop()
    except KeyboardInterrupt:
        # Exit without spewing an exception.
        pass
    sys.exit(0)


if __name__ == '__main__':
    run()
