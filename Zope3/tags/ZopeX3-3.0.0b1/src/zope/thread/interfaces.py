##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interfaces for zope.thread.

$Id$
"""

from zope.interface import Interface, Attribute


class IZopeThreadAPI(Interface):

    def thread_globals(thread=None):
        """Return the thread globals instance for the given thread.

        If thread is None, returns the globals for the current thread.
        """


class IInteractionThreadGlobal(Interface):

    interaction = Attribute("""IInteraction for the current thread.""")


class ISiteThreadGlobal(Interface):

    site = Attribute("""Site for the current thread.""")
