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
"""Pagelet interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component import ComponentLookupError
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.schema import Int
from zope.tales.interfaces import ITALESExpression

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.location import ILocation
from zope.app.publisher.interfaces.browser import IBrowserView


class PageletSlotLookupError(ComponentLookupError):
    """Pagelet slot object not found."""


class IPageletSlot(IInterface):
    """Marker interface for pagelet slots.

    The pagelet slot is used as a part ot the key for to register and
    collect pagelets.
    """


class IPagelet(IBrowserView):
    """Interface for custom pagelet adapters.

    Pagelets can be used in a page template as a piece of content rendered
    with it's own python view class. Yes with pagelets you can use more then
    one views in a pageltemplate. This let's pagelets act as portlets. The
    pagelet view can support content independent information where you can
    access in every page template on which the pagelet is registered.

    The meta directive set the 'weight' attribute to the class attribute
    '_weight'. If you whould like to use the settings from the meta directive
    point the attribute 'weight' to this default attribute.

    If you use a 'template', the meta directive sets the 'template' to the
    class attribute '_template'.
    """

    view = Attribute('The view the pagelet is used in.')

    slot = Attribute('The slot in which the pagelet is placed.')

    weight = Int(
        title=_(u'weight'),
        description=_(u"""
            Key for sorting pagelets if the pagelet collector is supporting
            this sort mechanism."""),
        required=False,
        default=0)


class ITALESPageletsExpression(ITALESExpression):
    """TAL namespace for getting a list of pagelets.

    To call pagelets in a view use the the following syntax in a page
    template::

      <tal:block repeat="pagelet pagelets:path.to.my.ISlot">
        <tal:block replace="structure pagelet" />
      </tal:block>

    where ``path.to.my.ISlot`` is a slot object that provides
    ``pagelet.interfaces.IPageletSlot``.
    """


class ITALESPageletExpression(ITALESExpression):
    """TAL namespace for getting a single pagelet.

    To call a named pagelet in a view use the the following syntax in a page
    template::

      <tal:block replace="structure pagelet:path.to.my.ISlot/name" />

    where ``path.to.my.ISlot`` is a slot object that provides
    ``pagelet.interfaces.IPageletSlot`` and ``name`` is the name of the page
    template .
    """
