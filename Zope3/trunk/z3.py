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

$Id: z3.py,v 1.18 2003/04/22 12:08:13 gvanrossum Exp $
"""

import os, sys, time

basepath = filter(None, sys.path)

def run(argv=sys.argv):
    # Record start times (real time and CPU time)
    t0 = time.time()
    c0 = time.clock()

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
    # See zope/app/startup/sitedefinition.py for this default:
    logging.root.setLevel(logging.INFO)
    # If log.ini exists, use it
    if os.path.exists("log.ini"):
        logging.config.fileConfig("log.ini")

    # temp hack
    dir = os.getcwd()

    # Copy products.zcml.in, if necessary
    if (not os.path.exists('products.zcml')
        and os.path.exists('products.zcml.in')
        ):
        cfin = open('products.zcml.in')
        cfout = open('products.zcml', 'w')
        cfout.write(cfin.read())
        cfout.close(); cfin.close()

    # Do global software config
    from zope.app import config
    config('site.zcml')

    # Load server config
    if (not os.path.exists('zserver.zcml')
        and os.path.exists('zserver.zcml.in')
        ):
        cfin = open('zserver.zcml.in')
        cfout = open('zserver.zcml', 'w')
        cfout.write(cfin.read())
        cfout.close(); cfin.close()

    from zope.configuration.xmlconfig import XMLConfig
    XMLConfig(os.path.join(dir, 'zserver.zcml'))()

    from zodb.zeo import threadedasync

    # Report total startup time
    t1 = time.time()
    c1 = time.clock()
    logging.info("Startup time: %.3f sec real, %.3f sec CPU", t1-t0, c1-c0)

    try:
        threadedasync.loop()
    except KeyboardInterrupt:
        # Exit without spewing an exception.
        pass
    sys.exit(0)


if __name__ == '__main__':
    run()
