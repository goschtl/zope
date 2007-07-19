##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: layer.py 75942 2007-05-24 14:53:46Z srichter $
"""
__docformat__="restructuredtext"

from z3c.form.interfaces import IFormLayer
from z3c.layer.pagelet import IPageletBrowserLayer
from jquery.layer import IJQueryJavaScriptBrowserLayer


class IDemoBrowserLayer(IFormLayer, IJQueryJavaScriptBrowserLayer, IPageletBrowserLayer):
    """Demo browser layer using div-form layout template."""
