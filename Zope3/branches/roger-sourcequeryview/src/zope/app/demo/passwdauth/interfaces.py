##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""/etc/passwd Authentication Plugin interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.schema import TextLine
from zope.app.i18n import ZopeMessageIDFactory as _

from zope.app.pluggableauth.interfaces import IPrincipalSource

class IFileBasedPrincipalSource(IPrincipalSource):
    """Describes file-based principal sources."""

    filename = TextLine(
        title = _(u'File Name'),
        description=_(u'File name of the data file.'),
        default = u'/etc/passwd')
