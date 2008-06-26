Encrypted Persistence
---------------------

This package also provides integration with persistent objects. Ususally,
objects are stored in the ZODB in plain text. The ``EncryptedPersistent`` base
class ensures that all data of the class is encrypted before being stored.

  >>> from z3c.encryptedpersistent import encryptedpersistent
  >>> class MyObject(encryptedpersistent.EncryptedPersistent):
  ...     name = None

  >>> myObj = MyObject()
  >>> myObj.name = u'Stephan Richter'


When an object is stored to a database, its ``__getstate__`` method is called:


  >> myObj.__getstate__()
  ('key1',
   "psHem+cmqG{(dp1\nS'name'\np2\nVStephan Richter\np3\nsS'__key__'\np4\nS'key1'\np5\ns.}")

When an object is loaded from the database, the state is passed into the
``__setstate__`` method:

  >> state = myObj.__getstate__()

  >>> myObj2 = MyObject()
  >>> myObj2.__setstate__(state)
  >>> myObj2.name
  u'Stephan Richter'

Let's now test this with a full database. Since we want to test, whether the
data is stored encrypted, we have to create a file:

  >>> import tempfile
  >>> dbFile = tempfile.mktemp('.fs')

Let's now add one of the encrypted persistent objects to the database:

  >>> from ZODB.DB import DB
  >>> from ZODB.FileStorage import FileStorage
  >>> db = DB(FileStorage(dbFile))
  >>> conn = db.open()
  >>> root = conn.root()

  >>> root['obj'] = myObj

  >>> import transaction
  >>> transaction.commit()

When the database is loaded again, the object's data is still there, ...

  >>> db.open().root()['obj'].name
  u'Stephan Richter'

and the data is truly encrypted in the file:

  >>> state[1] in open(dbFile).read()
  True
