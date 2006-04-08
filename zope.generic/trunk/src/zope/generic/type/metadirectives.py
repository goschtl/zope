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

from zope.configuration.fields import Bool
from zope.configuration.fields import GlobalInterface
from zope.configuration.fields import GlobalObject
from zope.interface import Interface

from zope.app.i18n import ZopeMessageFactory as _
from zope.generic.information.metadirectives import IBaseInformationDirective

    

class ITypeDirective(IBaseInformationDirective):
    """Declare attriubtes of the type directive.

    Register an type information and a type factory.
    """

    class_ = GlobalObject(
        title=_('Class'),
        description=_('Generic class implementation.'),
        required=True
        )



class IInitializerSubdirective(Interface):
    """Provide an initializer configuration for the type."""

    interface = GlobalInterface(
        title=_('Configuration interface'),
        description=_('Configuration interface defining the signature.'),
        required=False
        )

    handler = GlobalObject(
        title=_('Initializiation handler'),
        description=_('Callable (context, *pos, **kws).'),
        required=False
        )
