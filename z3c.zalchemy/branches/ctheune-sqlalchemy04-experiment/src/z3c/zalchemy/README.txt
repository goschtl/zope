=====================
SQLAlchemy and Zope 3
=====================

"z3c.zalchemy" integrates the object relational mapper SQLAlchemy into Zope 3
as SQLOS integrates sqlobject.

zalchemy tries to do its best not to interfere with the standard SQLAlchemy
usage.  The main part of zalchemy is the integration of the SQLAlchemy
transaction into the Zope transaction.  This is solved by using a data manager
which joins the Zope transaction for every newly created thread.

zalchemy uses the two phase commit system from zope.

This is how the two phase commit is used in zope.

    1. tpc_begin(txn)
    2. commit(txn)
    3. tpc_vote(txn)
    4. tpc_finish(txn)

  - commit does a session.flush() which actually executes all sql statements.
  - tpc_finish() does a transaction.commit() in the sqlalchemy transaction
  - tpc_abort() does a transaction.rollback() in the sqlalchemy transaction

If commit fails or another DataManager fails data is not commited to the
database.


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
here is, that the metadata from zalchemy must be used. Please note that you
need to call z3c.zalchemy.metadata.

  >>> import sqlalchemy
  >>> import z3c.zalchemy
  >>> table3 = sqlalchemy.Table(
  ...     'table3',
  ...     z3c.zalchemy.metadata(),
  ...     sqlalchemy.Column('id', sqlalchemy.Integer,
  ...         sqlalchemy.Sequence('atable_id'), primary_key=True),
  ...     sqlalchemy.Column('value', sqlalchemy.Integer),
  ...     )

Define a simple class which will be used later to map to a database table.

  >>> class A(object):
  ...     pass

Now we map the table to our class.

  >>> sqlalchemy.mapper(A, table3) is not None
  True

To let zalchemy do its work we need to register our database utility.

  >>> from z3c.zalchemy.interfaces import IAlchemyEngineUtility
  >>> from zope.component import provideUtility
  >>> provideUtility(engineUtility, IAlchemyEngineUtility)

Tables can be created without an open transaction or session.
If no session is created then the table creation is deferred to the next
call to zalchemy.getSession.

  >>> z3c.zalchemy.createTable('table3', '')

zalchemy automatically coordinates Zope's transaction manager with
SQLAlchemy's sessions. All mapped classes are automatically associated with
thread-local session, which in turn is automatically connected to a special
data manager that coordinates with Zope's transactions.

  >>> a = A()
  >>> a.value = 1

Committing a transaction will automatically trigger a flush and clear the
session.

  >>> import transaction
  >>> transaction.commit()

Now let's try to get the object back in a new transaction (we're in a new
transaction already because the old transaction was committed):

  >>> from z3c.zalchemy.datamanager import getSession as session
  >>> a = session().get(A, 1)
  >>> a.value
  1

  >>> transaction.commit()


Multiple databases
------------------

The above example assumed that there is only one database.  The database
engine was registered as an unnamed utility.  The unnamed utility is always
the default database for new sessions.

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

  >>> provideUtility(engine2Util, IAlchemyEngineUtility, name='engine2')

  >>> bTable = sqlalchemy.Table(
  ...     'bTable',
  ...     z3c.zalchemy.metadata(),
  ...     sqlalchemy.Column('id', sqlalchemy.Integer,
  ...         sqlalchemy.Sequence('btable_id'), primary_key=True),
  ...     sqlalchemy.Column('value', sqlalchemy.String),
  ...     )

  >>> class B(object):
  ...     pass
  >>> B.mapper = sqlalchemy.mapper(B, bTable)

Assign bTable to the new engine and create the table.
This time we do it inside of a session.

  >>> z3c.zalchemy.assignTable('bTable', 'engine2')
  >>> z3c.zalchemy.createTable('bTable', 'engine2')

  >>> b = B()
  >>> b.value = 'b1'

  >>> a = A()
  >>> a.value = 321

  >>> transaction.commit()

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

  >>> aa = Aa()
  >>> aa.value = 100

  >>> transaction.commit()


Tables With The Same Name In Different Databases
------------------------------------------------

IF we have two databases containing tables with the same name but with a
different structure we need to assign a table explicitely to a database. This
must be done by requesting metadata for a specific engine.

  >>> b2Table = sqlalchemy.Table(
  ...     'bTable',
  ...     z3c.zalchemy.metadata('b2Engine'),
  ...     sqlalchemy.Column('id', sqlalchemy.Integer,
  ...         sqlalchemy.Sequence('btable_id'), primary_key=True),
  ...     sqlalchemy.Column('b2value', sqlalchemy.String),
  ...     )

We can now request the table by providing the engine.

  >>> z3c.zalchemy.metadata.getTable('b2Engine', 'bTable', True)
  Table('bTable',...

If we have specified a table for the 'default' engine then we can request
'bTable' for 'b2Engine' with a fallback to the default engine.

  >>> z3c.zalchemy.metadata.getTable('b2Engine', 'table3', True)
  Table('table3',...

