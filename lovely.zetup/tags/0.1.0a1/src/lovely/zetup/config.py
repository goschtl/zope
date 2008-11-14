##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

import os
from logging.config import fileConfig
from zope.app.appsetup import appsetup
from interfaces import IConfig, IConfigurableSite, ISiteConfig
from zope import interface
from zope import component
import logging
import time

class Config(object):

    """Config objects are instantiated with a path to a python file.

    >>> Config('/notexistent')
    Traceback (most recent call last):
    ...
    ValueError: Config file not found '/notexistent'

    We need at least an app local in the file.

    >>> path = os.path.join(os.path.dirname(__file__), '__init__.py')
    >>> Config(path)
    Traceback (most recent call last):
    ...
    ValueError: No app dict in config '.../zetup/__init__.py'

    """
    interface.implements(IConfig)

    def __init__(self, path, withLogging=True):
        if not os.path.isfile(path):
            raise ValueError, "Config file not found %r" % path
        self.data = {}
        execfile(path, {}, self.data)
        if not 'app' in self.data:
            raise ValueError, "No app dict in config %r" % path
        t = time.time()
        self.path = os.path.abspath(path)
        self.dir = os.path.dirname(self.path)
        self.withLogging = withLogging
        self.setUpLogging()
        self.setUpZope()
        self.setUpSiteConfigs()
        logging.info('Configured Application %s' % (time.time()-t))

    def setUpZope(self):
        zcml = os.path.join(self.dir,
                            self.data['app']['zcml'])
        features = tuple(self.data['app'].get('features', ()))
        appsetup.config(zcml, features=features)

    def setUpLogging(self):
        path = self.data['app'].get('logging')
        if self.withLogging and path:
            cfg = os.path.join(self.dir, path)
            fileConfig(cfg)

    def setUpSiteConfigs(self):
        self.sites = self.data.get('sites', {})

class SiteConfig(object):

    component.adapts(IConfigurableSite)
    interface.implements(ISiteConfig)

    def __init__(self, context):
        self.context = context

    @property
    def config(self):
        gConfig = component.getUtility(IConfig)
        return gConfig.sites[self.context.__name__]

