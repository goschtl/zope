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
"""RML document.

$Id: interfaces.py 74195 2007-04-16 22:41:24Z srichter $
"""

import z3c.rmldocument.interfaces
import zope.interface


class Document(object):
    """An RML document definition."""

    zope.interface.implements(z3c.rmldocument.interfaces.IDocument)

    def __init__(self, template, fields=zope.interface.Interface,
                 blocks=zope.interface.Interface):
        self.template = template
        self.fields = fields
        self.blocks = blocks
