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

$Id: DTMLPageFields.py,v 1.1 2002/07/11 00:17:01 srichter Exp $
"""

from Zope.App.Formulator.FieldRegistry import getField
from Zope.App.Formulator.ValidatorRegistry import getValidator


SourceField = getField('StringField')(
    id = 'source',
    title = 'DTML Page Source',
    description = 'DTML Source Code',
    default = ''
    )
