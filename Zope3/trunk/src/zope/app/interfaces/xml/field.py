##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""

Revision information:
$Id: field.py,v 1.3 2003/04/10 09:05:12 faassen Exp $
"""
from zope.schema.interfaces import IBytes
from zope.schema import Bool

class IXML(IBytes):
    u"""A field that can store XML text.
    """

    check_wellformedness = Bool(
        title=u"Check for wellformedness",
        default=True)
    
    

