#############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

from five.grok.meta import ViewSecurityGrokker
import five.megrok.layout
import martian


class PageSecurityGrokker(ViewSecurityGrokker):
    """We want to set Zope 2 security on Pages
    """
    martian.component(five.megrok.layout.Page)


class FormSecurityGrokker(ViewSecurityGrokker):
    """We want to set Zope 2 security on Forms
    """
    martian.component(five.megrok.layout.Form)
