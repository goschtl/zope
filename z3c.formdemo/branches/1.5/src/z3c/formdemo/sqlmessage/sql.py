##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""SQL calls to database

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.rdb
from zope.rdb import interfaces

def query(query):
    db = zope.component.getUtility(interfaces.IZopeDatabaseAdapter, name='msg')
    conn = db()
    return zope.rdb.queryForResults(conn, query)

def initialize():
    query('''\
        CREATE TABLE msg (
            id INTEGER,
            who VARCHAR,
            when INTEGER,
            what VARCHAR)
        ''')

def queryAllMessages():
    return query('''\
        SELECT id, who, when, what FROM msg
        ''')

def getNextId():
    result = query('''\
        SELECT id FROM msg
        ''')
    if not result:
        return 0
    return max([entry.ID for entry in result]) + 1

def addMessage(data):
    query("""\
      INSERT INTO msg (id, who, when, what)
      VALUES (%(id)s, '%(who)s', %(when)s, '%(what)s')
        """ %data)

def updateMessage(id, data):
    data['id'] = id
    query("""\
        UPDATE msg
        SET who='%(who)s', when=%(when)s, what='%(what)s'
        WHERE id = %(id)s
        """ %data)

def getMessage(id):
    return query("""\
        SELECT id, who, when, what FROM msg WHERE id = %s
        """ %id)[0]

def deleteMessage(id):
    query("""\
    DELETE FROM msg WHERE id = %s
        """ %id)
