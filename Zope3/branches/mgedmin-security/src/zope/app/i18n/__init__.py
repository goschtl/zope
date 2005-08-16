##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Customization of zope.i18n for the Zope application server

$Id: __init__.py,v 1.5 2004/03/08 23:35:04 srichter Exp $
"""
from zope.i18n.messageid import MessageIDFactory

# Import _ to use to create message ids in the zope domain
ZopeMessageIDFactory = MessageIDFactory('zope')
