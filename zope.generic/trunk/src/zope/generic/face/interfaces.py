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

from zope.app.i18n import ZopeMessageFactory as _
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.schema import Object
from zope.schema import Text
from zope.schema import TextLine

from zope.generic.directlyprovides import IProvides



class IFaceType(IInterface):
    """Mark key or context interfaces."""



class IKeyfaceType(IFaceType):
    """Mark key interfaces.
    
    The key interface is the most relevant interface of the object in relation
    to a system domain."""



class IUndefinedKeyface(Interface):
    """A unspecified key interface."""

alsoProvides(IUndefinedKeyface, IKeyfaceType)



class IConfaceType(IFaceType):
    """Mark context interfaces.
    
    The context interface declares the context wherein information about an
    object should be catched.

    Context interfaces are *allways* pure marker interfaces. Utilities and 
    adapters providing this marker. Should provide IInformationProvider by
    adaption or implementation."""



class IUndefinedContext(Interface):
    """A unspecified context interface."""

alsoProvides(IUndefinedContext, IConfaceType)



class IFaced(Interface):
    """Assert that the key interface can be looked up.

    The key interface must be provided by adaption to IFace."""



class IFace(IFaced):
    """Declare the relevant key and context interface."""

    keyface = Object(
        title=_('Key interface'),
        description=_('Key interface of the underlying object.'),
        readonly=True,
        default=IUndefinedKeyface,
        schema=IKeyfaceType)

    conface = Object(
        title=_('Context interface'),
        description=_('Context interface of the underlying object.'),
        readonly=True,
        default=IUndefinedContext,
        schema=IConfaceType)



class IAttributeFaced(IFaced):
    """Store the key and context interface within an attribute.
    
    The context interface is provided by the attribute __conface__.
    The key interface is provided by the attribute  __keyface__.
    
    If no attribute is defined IUndefinedContext or IUndefinedKeyface will be returned.
    """

    __keyface__ = Object(
        title=_('Key interface'),
        description=_('Key interface of the assoziated object.'),
        readonly=True,
        default=IUndefinedKeyface,
        schema=IKeyfaceType)

    __conface__ = Object(
        title=_('Context interface'),
        description=_('Context interface of the assoziated object.'),
        readonly=True,
        default=IUndefinedContext,
        schema=IConfaceType)



class IProvidesAttributeFaced(IAttributeFaced, IProvides):
    """Directly provide the key and context interface."""


class IKeyfaceDescription(Interface):
    """Describe an key interface."""

    label = TextLine(title=_('Lable'))

    hint = Text(title=_('Hint'))



class IInformationProvider(IProvidesAttributeFaced):
    """Provide information to a dedicated context and key interface pair.

    Information provider will be registered as utility providing the context 
    interface and named by the dotted name of the key interface.

    Information providers can be extended by generic information mechanism
    such as zope.annotation.IAnnotations simply by adding a specific marker to
    the information provider implementation. The marker should invoke the 
    specific information mechanism:
    
        classProvides(api.InformationProvider, IAttributeAnnotatable)

        <class class="zope.generic.api.InformationProvider" >
            <implements="zope.annotation.IAttributeAnnotatable" />
        </class>
    """


class IGlobalInformationProvider(IInformationProvider):
    """Global information provider."""



class ILocalInformationProvider(IInformationProvider):
    """Local information provider."""
