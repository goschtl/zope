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
"""Wiki implementation

$Id: wiki.py,v 1.2 2004/02/24 16:51:15 philikon Exp $
"""
from zope.interface import implements
from zope.app.folder import Folder
from zope.products.zwiki.interfaces import IWiki


class Wiki(Folder):
    __doc__ = IWiki.__doc__

    implements(IWiki)
