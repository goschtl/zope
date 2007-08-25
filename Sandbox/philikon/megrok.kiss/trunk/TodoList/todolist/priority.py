import grok
from zope import component
from zope.app.catalog.interfaces import ICatalog
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

class PriorityVocabulary(grok.GlobalUtility):
    grok.implements(IVocabularyFactory)
    grok.name('Todo Priorities')

    def __call__(self, context):
        return SimpleVocabulary.fromValues(['important', 'medium', 'forgetit'])

class Priority(grok.Model):

    def __init__(self, priority):
        self.priority = priority

class Index(grok.View):

    def update(self):
        catalog = component.getUtility(ICatalog)
        self.todoitems = catalog.searchResults(
            priority={'any_of': (self.context.priority,)})
