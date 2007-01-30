=================
ZODB Mount Points
=================

A zodb mount point allows to transparently assign a zodb root object
to any persistent object. This object knows about its database by
using the multidatabase support of zope3.

    >>> from lovely.mount import root
    >>> import ZODB.tests.util, transaction
    >>> from zope import component
    >>> from ZODB.interfaces import IDatabase
    >>> databases = {}
    >>> db1 = ZODB.tests.util.DB(databases=databases, database_name='1')
    >>> db2 = ZODB.tests.util.DB(databases=databases, database_name='2')

    >>> component.provideUtility(db1, IDatabase, '1')
    >>> component.provideUtility(db2, IDatabase, '2')

Let us create a first root object with the first database.

And create a persistent object in the first database:

    >>> conn1 = db1.open()
    >>> p1 = ZODB.tests.util.P('1')
    >>> conn1.root()['root'] = p1

We have to commit here in order to get the connection.

    >>> transaction.commit()
    >>> conn1 = db1.open()
    >>> p1 = conn1.root()['root']

Let us set a dbroot object for the second database on the persistent
object of the first database. It can be instantiated with the database
name.

    >>> p1.dbroot = root.DBRoot('2')


It stores the database name.

    >>> p1.dbroot.dbName
    '2'

Now we can transparently use the mapping interface of the database
root object.

    >>> p1.dbroot['first'] = ZODB.tests.util.P('2.1')
    >>> p1.dbroot['first']
    P(2.1)

    >>> transaction.commit()

Now if we open the first database again we should get the persistent
object from the other database.

    >>> conn1 = db1.open()
    >>> p1 = conn1.root()['root']

The actual dbroot object is persistent in the first database.

    >>> p1.dbroot._p_jar.db().database_name
    '1'

    >>> p1.dbroot['first']._p_jar.db().database_name
    '2'
