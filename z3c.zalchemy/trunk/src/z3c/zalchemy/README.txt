=====================
SQLAlchemy and Zope 3
=====================

"z3c.zalchemy" integrates the object relational mapper SQLAlchemy into Zope 3
as SQLOS integrates sqlobject.

zalchemy tries to do its best not to interfere with the standard SQLAlchemy
usage.  The main part of zalchemy is the integration of the SQLAlchemy
transaction into the Zope transaction.  This is solved by using a data manager
which joins the Zope transaction for every newly created thread.


Important
=========

Zope uses the transaction module to handle transactions. zalchemy plugs into
this mechanism and uses its own data manager to use Zope's transaction module.

zalchemy provides the method z3c.zalchemy.getSession to obtain a SQLAlchemy
session object. This method makes sure the session is connected to Zope's
transactions.

Never get a session directly from SQLAlchemy!

It is also important to never store an instance of a session. Always directly
use z3c.zalchemy.getSession. This is necessary because you never know when
a transaction is commited. A commit always invalidates the current session.
A new call to getSession makes sure a new session is created.


zalchemy Class Implementation
=============================

There is no difference between the usage of SQLAlchemy together with Zope.

zalchemy provides a transparent way to connect a table to a database (engine).

A SQLAlchemy engine is represented as a utility:

  >>> from z3c.zalchemy.datamanager import AlchemyEngineUtility
  >>> engineUtility = AlchemyEngineUtility(
  ...       'database',
  ...       'sqlite:///%s'%dbFilename,
  ...       echo=False,
  ...       )

We create our table as a normal SQLAlchemy table. The important thing
here is, that the metadata from zalchemy must be used:

  >>> import sqlalchemy
  >>> import z3c.zalchemy
  >>> table3 = sqlalchemy.Table(
  ...     'table3',
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

  >>> sqlalchemy.mapper(A, table3) is not None
  True

To let zalchemy do its work we need to register our database utility.

  >>> from zope.component import provideUtility
  >>> provideUtility(engineUtility)

Tables can be created without an open transaction or session.
If no session is created then the table creation is deffered to the next
call to zalchemy.getSession.

  >>> z3c.zalchemy.createTable('table3')

Note that the transaction handling is done inside Zope.

  >>> import transaction
  >>> txn = transaction.begin()

Everything inside SQLAlchemy needs a Session. We must obtain the Session
from zalchemy. This makes sure that a transaction handler is inserted into
Zope's transaction process.

To simplify the usage of getSession we store the function in "session" (see
also the note above).

  >>> session = z3c.zalchemy.getSession

  >>> a = A()
  >>> a.value = 1

Apply the new object to the session :

  >>> session().save(a)

A new instance of a mapped sqlobject class is created. This object is not
stored in the database until the session is committed or flush is called for
the new instance.

To be able to query a new instance it is therefore necessary to flush the
object to the database before the query.

  >>> session().flush([a])

Commiting a transaction is doing the same with all remaining instances.
After this commit the current session is flushed and cleared.

  >>> transaction.commit()

Now let's try to get the object back in a new transaction :

  >>> txn = transaction.begin()

  >>> a = session().get(A, 1)
  >>> a.value
  1

  >>> transaction.commit()


Multiple databases
------------------

The above example asumed that there is only one database.
The database engine was registered as unnamed utility.
The unnamed utility is always the default database for new sessions.

This automatically assigns every table to the default engine.

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

Assign bTable to the new engine and create the table.
This time we do it inside of a session.

  >>> z3c.zalchemy.assignTable('bTable', 'engine2')
  >>> z3c.zalchemy.createTable('bTable')

  >>> b = B()
  >>> session().save(b)
  >>> b.value = 'b1'

  >>> a = A()
  >>> session().save(a)
  >>> a.value = 321

  >>> transaction.commit()

  >>> txn = transaction.begin()

  >>> a = session().get(A, 1)
  >>> b = session().get(B, 1)
  >>> str(b.value)
  'b1'

  >>> transaction.commit()

It is also possible to assign a class to a database :

  >>> class Aa(object):
  ...     pass
  >>> sqlalchemy.mapper(Aa, table3) is not None
  True

Now we can assign the class to the engine :

  >>> z3c.zalchemy.assignClass(Aa, 'engine2')

The problem is now that we do not have the table in 'engine2'.
We can use an additional parameter to createTable :

  >>> z3c.zalchemy.createTable('table3', 'engine2')

  >>> txn = transaction.begin()

  >>> aa = Aa()
  >>> session().save(aa)
  >>> aa.value = 100

  >>> transaction.commit()
