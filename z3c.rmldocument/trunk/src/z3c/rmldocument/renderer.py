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

import z3c.rml.rml2pdf
import z3c.rmldocument.interfaces
import zope.interface


class Renderer(object):
    """Render RML documents."""

    zope.interface.implements(z3c.rmldocument.interfaces.IDocumentRenderer)

    def render(self, document, fields=None, blocks=None):
        """Render the document with the given fields and blocks and
        return the PDF.
        """
        rml = document.template
        return z3c.rml.rml2pdf.parseString(rml).getvalue()
