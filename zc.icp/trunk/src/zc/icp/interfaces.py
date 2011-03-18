##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
__docformat__ = "reStructuredText"

import zope.interface

class IICPPolicy(zope.interface.Interface):
    """A policy to determine the response to an ICP request."""

    def __call__(url):
        """Inspect the given URL and return a mneumonic for an ICP opcode.

        The result can be one of the strings: 'ICP_OP_HIT', 'ICP_OP_MISS',
        'ICP_OP_ERR', 'ICP_OP_MISS_NOFETCH', and 'ICP_OP_DENIED'.
        """
