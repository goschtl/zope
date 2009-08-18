##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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
$Id$
"""

from zope.configuration.fields import GlobalInterface, GlobalObject, Path, \
    PythonIdentifier, Tokens
from zope.interface import Interface
from zope.location.interfaces import IRoot
from zope.schema import TextLine, BytesLine
from zope.security.zcml import Permission


class IPageDirective(Interface):
    """bobo:page directive"""

    name = TextLine(
        title=u'Name',
        required=True,
    )

    for_ = GlobalInterface(
        title=u"The interface this page is registered for",
        required=True,
    )

    class_ = GlobalObject(
        title=u"The browser view",
        required=True,
    )

    permission = Permission(
        title=u"Permission",
        required=False,
    )

    methods = Tokens(
        title=u'Allowed HTTP methods',
        value_type=BytesLine(
            required=True,
            constraint=lambda x: x in ('GET', 'POST', 'PUT', 'DELETE'),
        ),
        required=False,
        default=None,
    )

    attribute = PythonIdentifier(
        title=u"The name of the view attribute implementing the page.",
        required=False,
        default=u'__call__',
    )


class IResourcesDirective(Interface):
    """bobo:resources directive"""

    name = TextLine(
        title=u'Name',
        required=True,
    )

    for_ = GlobalInterface(
        title=u"The interface this resource is registered for",
        required=False,
        default=IRoot,
    )

    directory = Path(
        title=u"Resources path",
        required=True,
    )

    permission = Permission(
        title=u"Permission",
        required=False,
    )


class IResourceDirective(Interface):
    """bobo:resource directive"""

    name = TextLine(
        title=u'Name',
        required=True,
    )

    for_ = GlobalInterface(
        title=u"The interface this resource is registered for",
        required=False,
        default=IRoot,
    )

    file = Path(
        title=u"Resource path",
        required=True,
    )

    permission = Permission(
        title=u"Permission",
        required=False,
    )


class IDefaultViewDirective(Interface):
    """bobo:defaultView directive"""

    name = TextLine(
        title=u'Name',
        required=True,
    )

    for_ = GlobalInterface(
        title=u"The interface this page is for",
        required=True,
    )
