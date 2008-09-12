from grok.interfaces import IApplication
from zope.app.container.interfaces import IReadContainer

class IAppRoot(IApplication, IReadContainer):

    def getStore(self):
	""" Return the default store megrok.rdb.store """

    def delete(self, item):
	""" Delete item form store"""

    def add(self, item):
	""" Add item to the default store """

    def __delitem__(self, name):
	""" Delets the object with the pk-key name """

    def traverse(self, name):
	""" Traverses to db-objects using primary_key = name
	    as condition
	"""

    def filter(self, *args, **kwargs):
	""" Add kw arguments to that method this will turn 
	    the keywords in a where clause. You will get an
	    storm ResultSet as result.
	"""
