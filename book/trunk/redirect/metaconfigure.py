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
"""Directive Handlers

$Id$
"""
from zope.app.publisher.browser.viewmeta import page

class Redirect(object):
   """Redirects to a specified URL."""
   url = None

   def __call__(self):
       self.request.response.redirect(self.url)


def redirect(_context, name, url, permission, for_=None, layer='default'):
   
   # define the class that performs the redirect
   redirectClass = type(str("Redirect %s for %s to '%s'" %(name, for_, url)),
       (Redirect,), {'url' : url})
   
   page(_context, name, permission, for_, layer, class_=redirectClass)
