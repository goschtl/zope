# Copyright 2001-2002 Zope Corporation and Contributors.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.


from Interface import Interface
from Interface.Attribute import Attribute

class IStreamConsumer (Interface):
    """Consumes a data stream until reaching a completion point.

    The actual amount to be consumed might not be known ahead of time.
    """

    def received(data):
        """Accepts data, returning the number of bytes consumed."""

    completed = Attribute(
        'completed', 'Set to a true value when finished consuming data.')
