##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Schema package constructor

$Id: __init__.py,v 1.3 2002/10/04 18:24:55 jim Exp $
"""

from _Field import Field, Container, Iteratable, Orderable, Sized, Enumeratable
from _Field import Sequence
from _Field import Bytes, Text, Bool, Int, Float, Tuple, List, Dict, Datetime
from _Schema import validateMapping, validateMappingAll, getFields
