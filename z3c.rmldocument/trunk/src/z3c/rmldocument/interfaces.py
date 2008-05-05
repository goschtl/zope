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
"""User-editable RML documents interfaces.

$Id: interfaces.py 74195 2007-04-16 22:41:24Z srichter $
"""

import zope.interface


class IDocument(zope.interface.Interface):
    """A document.

    Documents have three degrees of flexibility:

    - A document-specific base template (PT) generating RML

    - Blocks of RML that can be embedded by the base template.

    - Fields of data that can be embedded by both the base template and the
      embedded RML blocks.

    """

    template = zope.interface.Attribute(
        "The page template for generating the basic RML.")

    field_schema = zope.interface.Attribute(
        "A schema describing which fields are available for substitution.")

    block_schema = zope.interface.Attribute(
        "A schema describing which blocks of RML are available")

    def renderRML(fields=None, blocks=None):
        """Return RML ready to be rendered."""
