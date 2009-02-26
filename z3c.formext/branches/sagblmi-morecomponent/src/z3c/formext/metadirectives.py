###############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""jsmodule meta directives

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.publisher.browser.metadirectives import IBasicResourceInformation
from zope.schema import TextLine
from zope.configuration.fields import Path, Tokens

class IJSModuleDirective(IBasicResourceInformation):
    """
    Defines a browser resource
    """

    name = TextLine(
        title=u"The name of the resource",
        description=u"""
        This is the name used in resource urls. Resource urls are of
        the form site/@@/resourcename, where site is the url of
        "site", a folder with a site manager.

        We make resource urls site-relative (as opposed to
        content-relative) so as not to defeat caches.""",
        required=False
        )

    namespace = TextLine(
        title=u"The namespace of the JavaScript module",
        description=u'''
        This is the namespace used to reference the javascript module
        in module loaders.  If not specified it will be extracted from
        the file by looking for Ext.ns("my.module.namespace");
        declarations.''',
        required=False
        )

    dependencies = Tokens(
        title=u"Other modules that this module depends on",
        description=u'''
        A whitespace-separated list of other modules that this module
        depends on.
        ''',
        value_type=TextLine(),
        required=False
        )

    file = Path(
        title=u"File",
        description=u"The file containing the JavaScript Module.",
        required=False
        )
