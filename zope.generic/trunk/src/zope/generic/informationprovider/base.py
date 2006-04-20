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

from zope.generic.configuration import IAttributeConfigurable
from zope.generic.keyface.api import KeyfaceDescription

from zope.generic.informationprovider import IInformationProvider



class InformationProvider(KeyfaceDescription):
    """Generic information provider.

    Information do relate a dedicated type of information marked as an interface
    extending IInformationProvider and another marker interface:

        >>> class ISpecialInformation(IInformationProvider):
        ...    pass

        >>> from zope.interface import Interface
        >>> class IFooMarker(Interface):
        ...    '''Foo is member of the example domain.'''

        >>> info = InformationProvider(IFooMarker, ISpecialInformation)

    The information will provide the interface of the dedicated information:

        >>> ISpecialInformation.providedBy(info)
        True

    The information is related to the interface declared by the interface
    attribute:

        >>> info.keyface == IFooMarker
        True
        >>> info.label
        u'IFooMarker'
        
        >>> info.hint
        u'Foo is member of the example domain.'


    Often you will provide a specific label and hint for the end-user:

        >>> info = InformationProvider(IFooMarker, ISpecialInformation, u'Foo', u'Bla bla.')
        >>> info.label
        u'Foo'
        
        >>> info.hint
        u'Bla bla.'
    """

    implements(IInformationProvider, IAttributeConfigurable, IAttributeAnnotatable)

    def __init__(self, keyface, provides, label=None, hint=None):
        super(InformationProvider, self).__init__(keyface, label, hint)
        alsoProvides(self, provides)