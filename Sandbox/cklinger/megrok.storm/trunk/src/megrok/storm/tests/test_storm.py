"""
  >>> from zope.component import getUtility
  >>> from zope.app.publisher.interfaces.browser import IBrowserMenu
  >>> from zope.publisher.browser import TestRequest
  >>> from storm.zope.interfaces import IZStorm

  Stores
  ------

  Get the named Store mydb

  >>> getUtility(IZStorm).get('mydb')
  <storm.store.Store object at ...>

  Get the default store megrok.storm.store

  >>> store = getUtility(IZStorm).get('megrok.storm.store')
  >>> store
  <storm.store.Store object at ...>

  Add a simple Table in the default store

  >>> store.execute("CREATE TABLE person (name VARCHAR(100), age Int(10))", noresult=True)
  >>> store.commit()

  The AppRoot for megrok.storm Applications 
  -----------------------------------------

  Setting up an Application

  >>> app = Application()
  >>> IAppRoot.providedBy(app)
  True

  >>> megrok.storm.directive.key.bind().get(app)
  'name'

  >>> megrok.storm.directive.rdb_object.bind().get(app)
  <class 'megrok.storm.tests.helper.Person'>

  The megrok.storm.AppRoot acts like a container
  ----------------------------------------------

  We can iterate over the megrok.storm.AppRoot like a container

  >>> [x for x in app]
  []

  We can also look at the len of our app
  
  >>> len(app)
  0

  We can add Person objects to the app_root
  
  >>> joe = Person()
  >>> joe.name=u"Joe"
  >>> joe.age=35
  >>> joe
  <megrok.storm.tests.helper.Person...>
  >>> app[u"joe"] = joe

  Now the len of our application should be one

  >>> len(app)
  1

  and we should find our object if we iterate about the app

  >>> [x for x in app]
  [<megrok.storm.tests.helper.Person object at ...>]

  We get the object with the container api

  >>> obj = app[u'joe']
  >>> obj
  <megrok.storm.tests.helper.Person...>

  >>> obj.name
  u'joe'
  >>> obj.age
  35

  >>> app.keys()
  [u'joe']

  >>> app.items()
  [<megrok.storm.tests.helper.Person object at ...>]

  Of course we can use our store to use pure SQL

  >>> obj = store.execute('select count(name) from person')
  >>> obj
  <storm.databases.sqlite.SQLiteResult object at ...>
  
  >>> obj.get_one()
  (1,)

  The filer api
  -------------

  First we create a second entry in the database

  >>> chris = Person()
  >>> chris.name = u"chris"
  >>> chris.age = 10
  >>> app.add(chris)

  We should find one chris

  >>> result = app.filter(name = u'chris')
  >>> result.count()
  1

  and we should find 0 tom´s

  >>> result = app.filter(name = u'tom')
  >>> result.count()
  0

  we schould find two objects which age > 0
  
  >>> result = app.filter('age' > 0)
  >>> result.count()
  2


  Deleteing an object
  -------------------

  >>> del app[u'joe']
  >>> len(app)
  1

"""
import grok
import megrok.storm
from zope.component import getUtility
from storm.zope.interfaces import IZStorm
from megrok.storm.tests.helper import Person
from megrok.storm.interfaces import IAppRoot

class MyDB(megrok.storm.Store):
    """ A Store which has the name 'mydb' """
    megrok.storm.storename('mydb')
    megrok.storm.uri('sqlite:')

class MegrokStormStore(megrok.storm.Store):
    """ A Default Store for ORM which has the name
        'megrok.storm.store' """
    megrok.storm.uri('sqlite:')

class Application(grok.Application, megrok.storm.AppRoot):
    megrok.storm.key('name')
    megrok.storm.rdb_object(Person)


def test_suite():
    from zope.testing import doctest
    from megrok.storm.tests import FunctionalLayer
    suite = doctest.DocTestSuite(optionflags=doctest.ELLIPSIS)
    suite.layer = FunctionalLayer
    return suite
