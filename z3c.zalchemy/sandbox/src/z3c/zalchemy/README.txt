=====================
SQLAlchemy and Zope 3
=====================

"z3c.zalchemy" integrates the object relational mapper sqlalchemy into
zope 3 as SQLOS integrates sqlobject.

zalchemy tries to do it's best not to interfere with the standard sqlalchemy
usage.
The main part of zalchemy is the integration of the sqlalchemy transaction
into the zope transaction.
This is solved by using a data manager which joins the zope transaction for
every newly created thread.


zalchemy class implementation
=============================

There is no difference between the usage of sqlalchemy together with zope.

zalchemy provides a transparent way to connect a table to a database (engine).

A SQLAlchemy engine is represented as a utility :

  >>> import os
  >>> from z3c.zalchemy.datamanager import AlchemyEngineUtility
  >>> engineUtil = AlchemyEngineUtility(
  ...     'sqlite',
  ...     dns='sqlite://',
  ...     )

We create our tables as usual sqlalchemy table : 

  >>> import sqlalchemy

  >>> aTable = sqlalchemy.Table(
  ...     'aTable',
  ...     sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
  ...     sqlalchemy.Column('value', sqlalchemy.Integer),
  ...     )

Note that by not specifying an engine we use a ProxyEngine which is
important here.  The real connection to database engine will be done
later in our utility.

  >>> aTable.engine
  <sqlalchemy.ext.proxy.ProxyEngine object at ...>

Define a simple class which will be used later to map to a database table.

  >>> class A(object):
  ...     pass

Now we map the table to our class.

  >>> sqlalchemy.assign_mapper(A, aTable)

The next step is to connect the table to the database engine.  We use
our utility for that. The ``create`` argument tells the utility if it
should try to create the table.

  >>> engineUtil.addTable(aTable,create=True)

To let zalchemy do his magic thing we need to register our database utility
as a named utility :

  >>> from zope.component import provideUtility
  >>> provideUtility(engineUtil, name='sqlite')

From now on zalchemy takes care of the zope transaction process behind the
scenes :
- connect the engine to the tables for every thread
- handle the two phase commit process
- disconnect the engine from the tables at the end of the thread

Note that the transaction handling is done inside zope.

  >>> import transaction
  >>> txn = transaction.begin()

Then we need to simulate a beforeTraversal Event :

  >>> from z3c.zalchemy.datamanager import beforeTraversal
  >>> beforeTraversal(None)

  >>> a = A()
  >>> a.value = 123

  >>> transaction.get().commit()

Now let's try to get the object back in a new transaction :

  >>> txn = transaction.begin()
  >>> beforeTraversal(None)

XXX this is not the same db, use filebased db?

  >>> a = A.get(1)
  >>> a.value
  123

  >>> transaction.get().commit()


Multiple databases
------------------

  >>> engine2Util = AlchemyEngineUtility(
  ...     'sqlite2',
  ...     dns='sqlite://',
  ...     )

  >>> engine = sqlalchemy.ext.proxy.ProxyEngine()
  >>> provideUtility(engine2Util, name='sqlite2')

  >>> bTable = sqlalchemy.Table(
  ...     'bTable',
  ...     sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
  ...     sqlalchemy.Column('value', sqlalchemy.String),
  ...     )
  >>> class B(object):
  ...     pass
  >>> sqlalchemy.assign_mapper(B, bTable)
  >>> engine2Util.addTable(bTable,create=True)

  >>> txn = transaction.begin()
  >>> beforeTraversal(None)

  >>> b = B()
  >>> b.value = 'b1'
  >>> B.get(1)

  >>> a = A()
  >>> a.value = 321

  >>> transaction.get().commit()

  >>> txn = transaction.begin()
  >>> beforeTraversal(None)

  >>> a = A.get(1)
  >>> b = B.get(1)
  >>> b.value
  u'b1'

  >>> transaction.get().commit()

Glitches
--------

  >>> txn = transaction.begin()
  >>> beforeTraversal(None)

  >>> startLen = A.mapper.count()

  >>> a1 = A()
  >>> a1.value = 123

  >>> A.mapper.count() == startLen + 1
  False

At this time a1 is not stored in the database. It is only stored when doing an
objectstore.commit().
At this time the object also has no id.

  >>> a1.id is None
  True

An explicit commit for a1 solves the problem :

  >>> sqlalchemy.objectstore.commit(a1)

  >>> A.mapper.count() == startLen + 1
  True
  >>> a1.id is None
  False

  >>> transaction.get().commit()


Exceptions
----------

A table must use a ProxyEngine.

  >>> illegalEngine = sqlalchemy.create_engine("sqlite://")

  >>> illegalTable = sqlalchemy.Table(
  ...     'illegalTable',
  ...     illegalEngine,
  ...     sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
  ...     sqlalchemy.Column('value', sqlalchemy.Integer),
  ...     )

  >>> engineUtil.addTable(illegalTable) #doctest: +ELLIPSIS
  Traceback (most recent call last):
  ...
  TypeError: ...

