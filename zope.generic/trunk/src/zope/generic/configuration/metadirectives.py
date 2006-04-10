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
from zope.configuration.fields import GlobalObject

from zope.generic.information.metadirectives import IBaseInformationDirective



class IConfigurationDirective(IBaseInformationDirective):
    """Declare configuration schema.

    Register configuration schema as interface utility typed by
    IConfigurationType within the configuration registry utility.    
    """



class IConfigurationHandlerDirective(IBaseInformationDirective):
    """Declare a public configuration handler.

    Register configuration handler as interface utility typed by
    IConfigurationHandlerType.
    
    """

    handler = GlobalObject(
        title=_('Configuration Handler'),
        description=_('Configuration handler or callable with the signature' +
                      '(componet, event, configuration=None, annotations=None).'),
        required=True
        )
