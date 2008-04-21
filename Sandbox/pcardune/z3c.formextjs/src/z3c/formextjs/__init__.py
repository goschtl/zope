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
"""ExtJS Form Integration Package

$Id$
"""

from zope.viewlet.viewlet import JavaScriptBundleViewlet
from zope.viewlet.viewlet import CSSViewlet


ExtJavaScriptViewlet = JavaScriptBundleViewlet(('ext/adapter/ext/ext-base.js',
                                               'ext/ext-all.js'))

ExtCSSViewlet = CSSViewlet('ext/resources/css/ext-all.css')
