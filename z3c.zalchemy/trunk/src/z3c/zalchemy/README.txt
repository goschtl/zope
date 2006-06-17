=====================
SQLAlchemy and Zope 3
=====================

"z3c.zalchemy" integrates the object relational mapper sqlalchemy into zope 3
as SQLOS integrates sqlobject.

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

  >>> from z3c.zalchemy.datamanager import AlchemyEngineUtility
  >>> engineUtility = AlchemyEngineUtility(
  ...       'database',
  ...       'sqlite:///%s'%dbFilename,
  ...       echo=False,
  ...       )

We create our table as usual sqlalchemy table :

  >>> import sqlalchemy
  >>> import z3c.zalchemy
  >>> aTable = sqlalchemy.Table(
  ...     'aTable',
  ...     z3c.zalchemy.metadata,
  ...     sqlalchemy.Column('id', sqlalchemy.Integer,
  ...         sqlalchemy.Sequence('atable_id'), primary_key=True),
  ...     sqlalchemy.Column('value', sqlalchemy.Integer),
  ...     redefine=True,
  ...     )

Define a simple class which will be used later to map to a database table.

  >>> class A(object):
  ...     pass

Now we map the table to our class.

  >>> sqlalchemy.mapper(A, aTable) is not None
  True

To let zalchemy do his magic thing we need to register our database utility.

  >>> from zope.component import provideUtility
  >>> provideUtility(engineUtility)

Tables can be created without an open transaction or session.
If no session is created then the table creation is deffered to the next
call to zalchemy.getSession.

  >>> z3c.zalchemy.createTable('aTable')

Note that the transaction handling is done inside zope.

  >>> import transaction
  >>> txn = transaction.begin()

Everything inside SQLAlchemy needs a Session. We must obtain the Session
from zalchemy. This makes sure that a transaction handler is inserted into
zope's transaction process.

  >>> session = z3c.zalchemy.getSession()

  >>> a = A()

Apply the new object to the session :

  >>> session.save(a)
  >>> a.value = 1

  >>> transaction.commit()

Now let's try to get the object back in a new transaction :
Note that it is neccessary to get a new session here.

  >>> txn = transaction.begin()
  >>> session = z3c.zalchemy.getSession()

  >>> a = session.get(A, 1)
  >>> a.value
  1

  >>> transaction.commit()


Multiple databases
------------------

The above example asumed that there is only one database.
The database engine was registered as unnamed utility.
The unnamed utility is always the default database for new sessions.

This automatically assign's every table to the default engine.

For multiple databases tables can be assigned to engines.

We create a new database engine :

  >>> engine2Util = AlchemyEngineUtility(
  ...     'engine2',
  ...     'sqlite:///%s'%dbFilename2,
  ...     echo=False,
  ...     )

Because there is already a default engine we must provide a name for the
new engine.

  >>> provideUtility(engine2Util, name='engine2')

  >>> bTable = sqlalchemy.Table(
  ...     'bTable',
  ...     z3c.zalchemy.metadata,
  ...     sqlalchemy.Column('id', sqlalchemy.Integer,
  ...         sqlalchemy.Sequence('btable_id'), primary_key=True),
  ...     sqlalchemy.Column('value', sqlalchemy.String),
  ...     redefine=True,
  ...     )

  >>> class B(object):
  ...     pass
  >>> B.mapper = sqlalchemy.mapper(B, bTable)

  >>> txn = transaction.begin()
  >>> session = z3c.zalchemy.getSession()

Assign bTable to the new engine and create the table.
This time we do it inside of a session.

  >>> z3c.zalchemy.assignTable('bTable', 'engine2')
  >>> z3c.zalchemy.createTable('bTable')

  >>> b = B()
  >>> session.save(b)
  >>> b.value = 'b1'

  >>> a = A()
  >>> session.save(a)
  >>> a.value = 321

  >>> transaction.commit()

  >>> txn = transaction.begin()
  >>> session = z3c.zalchemy.getSession()

  >>> a = session.get(A, 1)
  >>> b = session.get(B, 1)
  >>> str(b.value)
  'b1'

  >>> transaction.commit()

It is also possible to assign a class to a database :

  >>> class Aa(object):
  ...     pass
  >>> sqlalchemy.mapper(Aa, aTable) is not None
  True

Now we cann assign the class to the engine :

  >>> z3c.zalchemy.assignClass(Aa, 'engine2')

The problem is now that we do not have the table in 'engine2'.
We can use an additional parameter to createTable :

  >>> z3c.zalchemy.createTable('aTable', 'engine2')

  >>> txn = transaction.begin()
  >>> session = z3c.zalchemy.getSession()

  >>> aa = Aa()
  >>> session.save(aa)
  >>> aa.value = 100

  >>> transaction.commit()

