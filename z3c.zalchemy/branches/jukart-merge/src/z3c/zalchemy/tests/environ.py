##############################################################################
#
# Copyright (c) 2006 ROBOTECH Logistiksysteme GmbH and Contributors.
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

import sqlalchemy

engine = sqlalchemy.ext.proxy.ProxyEngine()

testTable = sqlalchemy.Table(
        'testTable',
        engine,
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True),
        sqlalchemy.Column('x', sqlalchemy.Integer),
        )

illegalTable = sqlalchemy.Table(
        'illegalTable',
        sqlalchemy.create_engine('sqlite://'),
        sqlalchemy.Column('id', sqlalchemy.Integer, primary_key = True),
        )
