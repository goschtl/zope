##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Common parameters for browser directives

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.configuration.fields
import zope.schema
import zope.i18nmessageid
_ = zope.i18nmessageid.MessageFactory('zope')

from zope.app.publisher.browser.fields import MenuField
from zope.app.security.fields import Permission

class IViewCharacteristics(zope.interface.Interface):

    for_ = zope.configuration.fields.GlobalObject(
        title=_(u'Registered for'),
        description=_(u"The interface or class this view is for."),
        required=False
        )

    layer = zope.configuration.fields.GlobalInterface(
        title=_('Layer'),
        description=_("""Layer that the view is registered for.
        This defaults to IDefaultBrowserLayer."""),
        required=False,
        )

    name = zope.schema.TextLine(
        title=_(u'Name'),
        description=_(u"""The name of a view, which will show up e.g. in
        URLs and other paths."""),
        required=True
        )

    permission = Permission(
        title=_(u'Permission'),
        description=_(u"The permission needed to use the view."),
        required=True
        )

class IRegisterInMenu(zope.interface.Interface):

    menu = MenuField(
        title=_(u'Menu'),
        description=_(u"A browser menu to include the page in."),
        required=False
        )

    title = zope.configuration.fields.MessageID(
        title=_(u'Menu label'),
        description=_(u"""The browser menu label for the page. Must be
        supplied when the 'menu' attribute is supplied."""),
        required=False
        )
