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
"""XXX short summary goes her

XXX longer description goes here.

$Id: Util.py,v 1.2 2002/07/01 14:40:04 k_vertigo Exp $
"""

import Row
import ResultSet

def query_for_results(conn, query):

    # need to typing
    cursor = conn.cursor()
    cursor.execute(query)

    columns = [c[0] for c in cursor.description]

    row_klass = Row.row_class_factory(columns)
    
    return ResultSet(columns,
                     cursor.fetchall(),
                     row_klass)






