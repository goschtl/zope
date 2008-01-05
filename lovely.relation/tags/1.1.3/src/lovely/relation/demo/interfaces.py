##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = "reStructuredText"

from zope import schema, interface

class IRelatedByDocument(interface.Interface):

    """things that can be refered to by documents, we use a vocabulary
    here in order to work with existing widgets."""

    backrefs = schema.List(
            title=u"Backreferences",
            value_type=schema.Choice(vocabulary='demo.documentsInParent'),
            required=False, default=[],
            readonly=True)

class IDocument(IRelatedByDocument):
    related = schema.List(
            title=u"Related",
            value_type=schema.Choice(vocabulary='demo.documentsInParent'),
            required=False,
            default=[])

