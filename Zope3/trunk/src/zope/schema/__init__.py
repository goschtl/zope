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

$Id: __init__.py,v 1.10 2003/04/14 18:21:36 fdrake Exp $
"""

from zope.schema._field import Field, Container, Iterable, Orderable
from zope.schema._field import MinMaxLen, Enumerated, Sequence
from zope.schema._field import Bytes, BytesLine
from zope.schema._field import Text, TextLine, Bool, Int, Float, Tuple, List
from zope.schema._field import Password, Dict, Datetime, SourceText
from zope.schema._field import EnumeratedTextLine, EnumeratedInt
from zope.schema._field import EnumeratedDatetime, EnumeratedFloat
from zope.schema._schema import getFields, getFieldsInOrder
from zope.schema._schema import getFieldNames, getFieldNamesInOrder
from zope.schema.accessors import accessors

# XXX backward compatibility; to be removed within a week
ValueSet = Enumerated
