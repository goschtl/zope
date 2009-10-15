===================
z3c.multifieldindex
===================

This package provides an index for zope catalog that can index multiple fields.
It is useful in cases when field set are dynamic (for example with customizable
persistent fields).

Actually, this package provides a base class for custom multi-field indexes and
to make it work, you need to override some methods in it. But first, let's
create a content schema and interface we will use:

  >>> from zope.interface import Interface, implements
  >>> from zope.schema import Text, Int, List, TextLine
  
  >>> class IPerson(Interface):
  ...
  ...     age = Int()
  ...     info = Text()
  ...     skills = List(value_type=TextLine())

  >>> class Person(object):
  ...
  ...     implements(IPerson)
  ...
  ...     def __init__(self, age, info, skills):
  ...         self.age = age
  ...         self.info = info
  ...         self.skills = skills

Let's create a set of person objects:

  >>> dataset = [
  ...     (1, Person(20, u'Sweet and cute', ['dancing', 'singing'])),
  ...     (2, Person(33, u'Smart and sweet', ['math', 'dancing'])),
  ...     (3, Person(6, u'Young and cute', ['singing', 'painting'])),
  ... ]

We have choose exactly those different types of fields to illustrate that the
index is smart enough to know how to index each type of value. We'll return
back to this topic later in this document.

Now, we need to create an multi-field index class that will be used to index our
person objects. We'll override two methods in it to make it functional:

  >>> from z3c.multifieldindex.index import MultiFieldIndexBase
  >>> from zope.schema import getFields

  >>> class PersonIndex(MultiFieldIndexBase):
  ...
  ...     def _fields(self):
  ...         return getFields(IPerson).items()
  ... 
  ...     def _getData(self, object):
  ...         return {
  ...             'age': object.age,
  ...             'info': object.info,
  ...             'skills': object.skills,
  ...         }

The "_fields" method should return an iterable of (name, field) pairs of fields
that should be indexed. The sub-indexes will be created for those fields.

The "_getData" method returns a dictionary of data to be indexed using given
object. The keys of the dictionary should match field names.

Sub-indexes are created automatically by looking up an index factory for each
field. Three most-used factories are provided by this package. Let's register
them to continue (it's also done in this package's configure.zcml file):

  >>> from z3c.multifieldindex.subindex import DefaultIndexFactory
  >>> from z3c.multifieldindex.subindex import CollectionIndexFactory
  >>> from z3c.multifieldindex.subindex import TextIndexFactory
  >>> from zope.component import provideAdapter
  
  >>> provideAdapter(DefaultIndexFactory)
  >>> provideAdapter(CollectionIndexFactory)
  >>> provideAdapter(TextIndexFactory)

The default index factory creates zc.catalog's ValueIndex, the collection index
factory creates zc.catalog's SetIndex and the text index factory creates
zope.index's TextIndex. This is needed to know when you'll be doing queries.

Okay, now let's create an instance of index and prepare it to be used.

  >>> index = PersonIndex()
  >>> index.recreateIndexes()

The "recreateIndexes" does re-creation of sub-indexes. It is normally called
by a subscriber to IObjectAddedEvent, provided by this package, but we simply
call it by hand for this test.

Now, let's finally index our person objects:

  >>> for docid, person in dataset:
  ...     index.index_doc(docid, person)

Let's do a query now. The query format is quite simple. It is a dictionary, where
keys are names of fields and values are queries for sub-indexes.

  >>> results = index.apply({
  ...     'skills': {'any_of': ('singing', 'painting')},
  ... })
  >>> list(results)
  [1, 3]

  >>> results = index.apply({
  ...     'info': 'sweet',
  ... })
  >>> list(results)
  [1, 2]

  >>> results = index.apply({
  ...     'age': {'between': (1, 30)},
  ... })
  >>> list(results)
  [1, 3]

  >>> results = index.apply({
  ...     'age': {'between': (1, 30)},
  ...     'skills': {'any_of': ('dancing', )},
  ... })
  >>> list(results)
  [1]
