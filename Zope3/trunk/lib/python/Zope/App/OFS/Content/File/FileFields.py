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

$Id: FileFields.py,v 1.2 2002/06/10 23:27:57 jim Exp $
"""

from Zope.App.Formulator.FieldRegistry import getField
from Zope.App.Formulator.ValidatorRegistry import getValidator


ContentTypeField = getField('StringField')(
    id = 'contentType',
    title = 'Content Type',
    description = 'The content type identifies the type of data.',
    default = 'text/plain',
    )


DataField = getField('FileField')(
    id = 'data',
    title = 'Data',
    description = 'The actual content of the object.',
    )
