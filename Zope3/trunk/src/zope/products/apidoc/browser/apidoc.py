##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Main API Documentation View

$Id: apidoc.py,v 1.1 2004/01/29 17:51:14 srichter Exp $
"""
from zope.products.apidoc.utilities import stx2html


class APIDocumentation(object):
    """View for the API Documentation"""

    def getModuleList(self):
        """Get a list of all available documentation modules."""
        modules = []
        items = list(self.context.items())
        items.sort()
        return [{'name': name,
                 'title': m.title,
                 'description': stx2html(m.description)}
                for name, m in items ]
