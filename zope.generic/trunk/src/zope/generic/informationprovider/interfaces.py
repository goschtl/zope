##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

__docformat__ = 'restructuredtext'

from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import Interface
from zope.schema import Text
from zope.schema import TextLine

from zope.generic.configuration import IAttributeConfigurable
from zope.generic.configuration import IConfigurable
from zope.generic.face import IProvidesAttributeFaced


class IInformable(IConfigurable, IAnnotatable):
    """Provide generic mechanism to access or attach information to the object."""



class IAttributeInformable(IInformable, IAttributeConfigurable, IAttributeAnnotatable):
    """Provide generic mechanism to access or attach information to the object."""



class IInformationProvider(IInformable, IProvidesAttributeFaced):
    """Provide information to a dedicated context and key interface pair.

    Information provider will be registered as utility providing the context 
    interface and named by the dotted name of the key interface.

    """


class IGlobalInformationProvider(IInformationProvider):
    """Global information provider."""



class ILocalInformationProvider(IInformationProvider):
    """Local information provider."""



class IUserDescription(Interface):
    """Description for an user."""

    label = TextLine(title=_('Lable'))

    hint = Text(title=_('Hint'))
