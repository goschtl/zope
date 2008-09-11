##############################################################################
#
# Copyright (c) 2006-2008 Lovely Systems GmbH. All Rights Reserved.
#
# This software is subject to the provisions of the Lovely Visible Source
# License, Version 1.0 (LVSL).  A copy of the LVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
$Id$
"""
__docformat__ = 'restructuredtext'

import re

from zope import component

from zope.testing.loggingsupport import InstalledHandler

from lovely.responsecache.purge import log, PurgeUtil
from lovely.responsecache.interfaces import IPurge


_purgeOriginal = PurgeUtil._purgeURLs.im_func

def _purgeTesting(self, urls):
    for url in urls:
        log.info('purged %r', url)
    return True

REMOVE_LINES = re.compile('lovely.responsecache.purge.*\n')

class PurgeInfo(object):

    def __init__(self, log_info):
        self.log_info = log_info

    def __call__(self):
        result = str(self.log_info)
        self.log_info.clear()
        return REMOVE_LINES.sub('', result)


def setUpPurge(test):
    PurgeUtil._purgeURLs = _purgeTesting

    log_info = InstalledHandler('lovely.responsecache.purge')
    test.globs['log_info'] = log_info
    test.globs['purgeInfo'] = PurgeInfo(log_info)

    purgeUtil = component.getUtility(IPurge)
    purgeUtil.failLock.acquire()
    purgeUtil.failedHosts.clear()
    purgeUtil.failLock.release()


def tearDownPurge(test):
    PurgeUtil._purgeURLs = _purgeOriginal

