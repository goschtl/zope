##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Service Manager code

$Id$
"""
__docformat__ = "reStructuredText"
from zope.deprecation import deprecated

from zope.app.component.site import SiteManager, UtilityRegistration
from zope.app.component.interfaces.registration import \
     IRegisterableContainerContaining as IRegisterableContainerContainer

deprecated(('SiteManager', 'UtilityRegistration'),
           'This class has been moved to zope.app.component.site. '
           'The reference will be gone in X3.3.')

deprecated('IRegisterableContainerContainer',
           'This interface has been moved to zope.app.component.interfaces '
           'and been renamed to IRegisterableContainerContaining. '
           'The reference will be gone in X3.3.')

ServiceManager = SiteManager

ServiceRegistration = UtilityRegistration

deprecated(('ServiceManager', 'ServiceRegistration'),
           'The concept of services has been removed. Use utilities instead. '
           'The reference will be gone in X3.3.')
