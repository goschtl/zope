##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Functions that control how the Zope appserver knits itself together.

$Id$
"""
import logging
import os
import sys
import time

from zdaemon import zdoptions

import twisted.web2.wsgi
import twisted.web2.server
from twisted.application import service
from twisted.internet import reactor

from zope.event import notify

import zope.app.appsetup
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
from zope.app import wsgi
from zope.app.twisted import log

CONFIG_FILENAME = "zope.conf"

# We need some out-of-band communication between twisteds reactor and the
# zdaemon.
should_restart = False

class ZopeOptions(zdoptions.ZDOptions):

    logsectionname = None

    def default_configfile(self):
        dir = os.path.normpath(
            os.path.join(os.path.dirname(__file__),
                         os.pardir, os.pardir, os.pardir, os.pardir))
        for filename in [CONFIG_FILENAME, CONFIG_FILENAME + ".in"]:
            filename = os.path.join(dir, filename)
            if os.path.isfile(filename):
                return filename
        return None


class ZopeService(service.MultiService):

    def startService(self):
        notify(zope.app.appsetup.interfaces.ProcessStarting())
        service.MultiService.startService(self)

    # can override stopService or similar to implement shutdown event later.


def main(args=None):
    global should_restart
    # Record start times (real time and CPU time)
    t0 = time.time()
    c0 = time.clock()

    service = setup(load_options(args))
    service.startService()
    reactor.addSystemEventTrigger('before', 'shutdown', service.stopService)

    t1 = time.time()
    c1 = time.clock()
    logging.info("Startup time: %.3f sec real, %.3f sec CPU", t1-t0, c1-c0)

    reactor.run()

    # zdaemon will restart the process if it exits with an error
    if should_restart:
        sys.exit(1)
    else:
        sys.exit(0)


def debug(args=None):
    options = load_options(args)

    zope.app.appsetup.config(options.site_definition)

    db = zope.app.appsetup.appsetup.multi_database(options.databases)[0][0]
    notify(zope.app.appsetup.interfaces.DatabaseOpened(db))

    return db


def load_options(args=None):
    if args is None:
        args = sys.argv[1:]
    options = ZopeOptions()
    options.schemadir = os.path.dirname(os.path.abspath(__file__))
    options.realize(args)
    options = options.configroot

    if options.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.path]
    return options


def setup(options):
    sys.setcheckinterval(options.check_interval)

    zope.app.appsetup.product.setProductConfigurations(
        options.product_config)
    options.eventlog()
    options.accesslog()
    for logger in options.loggers:
        logger()

    # Setup the logs. Eventually this might be better done using utilities.
    twisted.python.log.addObserver(log.PythonLoggingObserver())
    observer = log.CommonAccessLoggingObserver()
    observer.start()

    features = ('twisted',)
    # Provide the devmode, if activated
    if options.devmode:
        features += ('devmode',)
        logging.warning("Developer mode is enabled: this is a security risk "
            "and should NOT be enabled on production servers. Developer mode "
            "can be turned off in etc/zope.conf")

    zope.app.appsetup.config(options.site_definition, features=features)

    db = zope.app.appsetup.appsetup.multi_database(options.databases)[0][0]

    notify(zope.app.appsetup.interfaces.DatabaseOpened(db))

    # Set number of threads
    reactor.suggestThreadPoolSize(options.threads)

    rootService = ZopeService()

    for server in options.servers + options.sslservers + options.sshservers:
        service = server.create(db)
        service.setServiceParent(rootService)

    return rootService
