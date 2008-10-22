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
"""Grokkers that look for description providers in the framework.
"""
import martian

class priority(martian.Directive):
    """Determine in which order your descriptor provider should be applied.

    The order is a number up to 1000.

    This is important, because the descriptor finder will ask the
    descriptors in the order of their priorities whether they are
    willing to handle a certain object and normally it will return the
    first one, that agreed to do this.

    The more little the number is, the earlier your description
    provider will appear in the list of all providers. The builtin
    providers all have a range above 900.

    The most basic description provider
    (``SimpleDescriptionProvider``) registers with an order number of
    1001 and handles every object.
    """
    scope = martian.CLASS
    store = martian.ONCE
    default = 500
