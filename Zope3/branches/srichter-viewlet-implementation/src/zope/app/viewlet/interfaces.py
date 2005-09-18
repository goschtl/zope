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
"""Viewlet interfaces

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


class ViewletRegionLookupError(ComponentLookupError):
    """Viewlet region object not found."""


class IViewletRegion(IInterface):
    """Marker interface for viewlet regions.

    The viewlet region is used as a part ot the key for to register and
    collect viewlets.
    """


class IViewlet(IBrowserView):
    """Interface for custom viewlet adapters.

    Viewlets can be used in a page template as a piece of content rendered
    with it's own python view class. Yes with viewlets you can use more then
    one views in a pageltemplate. This let's viewlets act as portlets. The
    viewlet view can support content independent information where you can
    access in every page template on which the viewlet is registered.

    The meta directive set the 'weight' attribute to the class attribute
    '_weight'. If you whould like to use the settings from the meta directive
    point the attribute 'weight' to this default attribute.

    If you use a 'template', the meta directive sets the 'template' to the
    class attribute '_template'.
    """

    view = Attribute('The view the viewlet is used in.')

    region = Attribute('The region in which the viewlet is placed.')

    weight = Int(
        title=_(u'weight'),
        description=_(u"""
            Key for sorting viewlets if the viewlet collector is supporting
            this sort mechanism."""),
        required=False,
        default=0)


class ITALESViewletsExpression(ITALESExpression):
    """TAL namespace for getting a list of viewlets.

    To call viewlets in a view use the the following syntax in a page
    template::

      <tal:block repeat="viewlet viewlets:path.to.my.IRegion">
        <tal:block replace="structure viewlet" />
      </tal:block>

    where ``path.to.my.IRegion`` is a region object that provides
    ``viewlet.interfaces.IViewletRegion``.
    """


class ITALESViewletExpression(ITALESExpression):
    """TAL namespace for getting a single viewlet.

    To call a named viewlet in a view use the the following syntax in a page
    template::

      <tal:block replace="structure viewlet:path.to.my.IRegion/name" />

    where ``path.to.my.IRegion`` is a region object that provides
    ``viewlet.interfaces.IViewletRegion`` and ``name`` is the name of the page
    template .
    """
