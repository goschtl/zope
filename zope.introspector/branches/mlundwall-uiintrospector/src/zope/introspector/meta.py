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
from descriptionprovider import (DescriptionProvider, descriptor_registry,)

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

class DescriptionProviderGrokker(martian.ClassGrokker):
    martian.component(DescriptionProvider)
    martian.directive(priority)
    def execute(self, klass, priority, *args, **kw):
        num = 0
        found = False
        for num in range(0, len(descriptor_registry)):
            if descriptor_registry[num]['priority'] >= priority:
                found = True
                break
        if not found and num:
            num += 1
        descriptor_registry.insert(num, dict(handler=klass,
                                             priority=priority))
        return True
