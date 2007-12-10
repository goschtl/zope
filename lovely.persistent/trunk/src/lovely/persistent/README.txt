==========
Persistent
==========

This package provides a base class for persistent objects with the advantage
that the object is only marked as changed if an attribute has really changed.

  >>> import transaction
  >>> from ZODB.tests.util import DB

  >>> from lovely import persistent

  >>> p = LovelyPersistent()
  >>> p._p_changed
  False

  >>> p.a = 1
  >>> db = DB()
  >>> conn = db.open()
  >>> conn.root()['p'] = p
  >>> transaction.commit()

After commiting the changes the object is no longer in changed state.

  >>> p._p_changed
  False

Setting a with its existing value doesn't put the object in cahnged state.

  >>> p.a
  1
  >>> p.a = 1
  >>> p._p_changed
  False

But modifying a :

  >>> p.a = 2
  >>> p._p_changed
  True
  >>> transaction.commit()

  >>> p._p_changed
  False

Deleting an attribute also put the object into changed state.

  >>> del p.a
  >>> p._p_changed
  True


Special Properties
==================

Special property implementations do work too. To show this we use the
fieldproperties from zope.schema.

  >>> from zope.schema.fieldproperty import FieldProperty
  >>> from zope import schema, interface
  >>> class IMyFace(interface.Interface):
  ...     eyesOpen = schema.Bool(default=True, required=False)

  >>> class MyFace(persistent.Persistent):
  ...     eyesOpen = FieldProperty(IMyFace['eyesOpen'])

  >>> persistent.tests.MyFace = MyFace
  >>> MyFace.__module__ = persistent.tests.setUp.__module__
  >>> myFace = conn.root()['myFace'] = MyFace()
  >>> transaction.commit()

Default values.

  >>> myFace.eyesOpen
  True

Validation.

  >>> myFace.eyesOpen = 'not always'
  Traceback (most recent call last):
  ...
  WrongType: ('not always', <type 'bool'>)

Note, setting to default value does not change the object.

  >>> transaction.commit()
  >>> myFace.eyesOpen = True
  >>> myFace._p_changed
  False

  >>> transaction.commit()
  >>> myFace.eyesOpen = False
  >>> myFace._p_changed
  True


