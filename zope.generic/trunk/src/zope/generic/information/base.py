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

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import alsoProvides
from zope.interface import implements

from zope.generic.component.api import toDottedName
from zope.generic.component.api import KeyInterfaceDescription
from zope.generic.configuration import IAttributeConfigurable

from zope.generic.information import IInformation




class Information(KeyInterfaceDescription, dict):
    """Default information.

    Information do relate a dedicated type of information marked as an interface
    extending IInformation and another marker interface:

        >>> class ISpecialInformation(IInformation):
        ...    pass

        >>> from zope.interface import Interface
        >>> class IFooMarker(Interface):
        ...    '''Foo is member of the example domain.'''

        >>> info = Information(IFooMarker, ISpecialInformation)

    The information will provide the interface of the dedicated information:

        >>> ISpecialInformation.providedBy(info)
        True

    The information is related to the interface declared by the interface
    attribute:

        >>> info.interface == IFooMarker
        True
        >>> info.label
        u'IFooMarker'
        
        >>> info.hint
        u'Foo is member of the example domain.'


    Often you will provide a specific label and hint for the end-user:

        >>> info = Information(IFooMarker, ISpecialInformation, u'Foo', u'Bla bla.')
        >>> info.label
        u'Foo'
        
        >>> info.hint
        u'Bla bla.'
    """

    implements(IInformation, IAttributeConfigurable, IAttributeAnnotatable)

    def __init__(self, interface, provides, label=None, hint=None):
        super(Information, self).__init__(interface, label, hint)
        alsoProvides(self, provides)

