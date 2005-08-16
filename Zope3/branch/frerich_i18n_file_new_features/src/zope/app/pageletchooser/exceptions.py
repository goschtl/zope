##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""PageletChooser exceptions

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component import ComponentLookupError

from zope.app.i18n import ZopeMessageIDFactory as _



class PageletVocabularyInterfaceLookupError(ComponentLookupError):
    """Pagelet vocabulary interface not found."""

PageletError_vocabulary_interface_not_found = _(
    u'Pagelet vocabulary interface not found.')
