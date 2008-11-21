##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

$Id: __init__.py 3799 2008-11-14 07:46:44Z fafhrd91 $
"""
from zope.app.generations.generations import SchemaManager

schemaManager = SchemaManager(
    minimum_generation=0,
    generation=0,
    package_name='z3ext.skintool.generations')
