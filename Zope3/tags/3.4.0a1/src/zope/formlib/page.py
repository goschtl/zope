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
"""Simple Page support

This module has been deprecated and will be gone in Zope 3.5.

$Id$
"""
# BBB 2006/04/19 -- to be removed after 12 months
import zope.deferredimport
zope.deferredimport.deprecated(
    "It has moved to zope.publisher.browser.BrowserPage.  This reference "
    "will be gone in Zope 3.5.",
    Page = 'zope.publisher.browser:BrowserPage',
    )
