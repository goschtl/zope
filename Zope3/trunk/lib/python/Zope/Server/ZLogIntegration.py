# Copyright 2001-2002 Zope Corporation and Contributors.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
"""Makes asyncore log to zLOG.
"""

from zLOG import LOG, register_subsystem, BLATHER, INFO, WARNING, ERROR
register_subsystem('ZServer')
severity={'info':INFO, 'warning':WARNING, 'error': ERROR}

def log_info(self, message, type='info'):
    LOG('Zope.Server', severity[type], message)

import asyncore
asyncore.dispatcher.log_info=log_info
