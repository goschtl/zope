##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Directive Interfaces

$Id$
"""
from zope.interface import Interface
from zope.configuration.fields import GlobalObject
from zope.schema import Id, TextLine

class IRedirectDirective(Interface):
   """Redirects clients to a specified URL."""

   name = TextLine(
       title=u"Name",
       description=u"The name of the requested view.")

   for_ = GlobalObject(
       title=u"For Interface",
       description=u"The interface the directive is used for.",
       required=False)

   url = TextLine(
       title=u"URL",
       description=u"The URL the client should be redirected to.")

   permission = Id(
       title=u"Permission",
       description=u"The permission needed to access the view.")

   layer = TextLine(
       title=u"Layer",
       description=u"The layer the redirect is defined in.",
       required=False)
