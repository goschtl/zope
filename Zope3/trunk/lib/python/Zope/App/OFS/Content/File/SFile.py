##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: SFile.py,v 1.1 2002/07/19 13:12:31 srichter Exp $
"""
import Schema


class SFile(Schema.Schema):

    contentType = Schema.Str(
        id = 'contentType',
        title = 'Content Type',
        description = 'The content type identifies the type of data.',
        default = 'text/plain',
        )


    data = Schema.Str(
        id = 'data',
        title = 'Data',
        description = 'The actual content of the object.',
        )
