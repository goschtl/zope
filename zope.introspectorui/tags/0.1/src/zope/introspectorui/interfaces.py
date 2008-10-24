##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Interfaces for zope.introspectorui.
"""
from zope.interface import Interface
from grokcore.view.interfaces import IGrokView

class ICodeView(IGrokView):
    """Views that display code.
    """

class IBreadcrumbProvider(Interface):
    """Breadcrumb providers provide breadcrumbs for objects.
    """

    def getBreadcrumbs():
        """Provide HTML cod containing breadcrumbs.
        """
