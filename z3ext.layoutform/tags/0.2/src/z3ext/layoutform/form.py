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
"""Support for Layout Templates

$Id$
"""
from zope import interface

from z3c.form import form
from z3ext.layout.pagelet import BrowserPagelet

from interfaces import IPageletForm


class PageletForm(form.Form, BrowserPagelet):
    interface.implements(IPageletForm)

    render = BrowserPagelet.render
    __call__ = BrowserPagelet.__call__
