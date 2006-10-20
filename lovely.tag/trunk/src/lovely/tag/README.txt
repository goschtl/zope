=======
Tagging
=======

A tagging engine allows you to assign tags to any type of object by an user. A
tag is a simple string.

  >>> from lovely import tag

Tagging Engine
--------------

The tagging engine provides the capabilities to manipulate and and query
tagged items.

  >>> engine = tag.TaggingEngine()
  >>> engine
  <TaggingEngine entries=0>

The first step is to associate tags with an item for a user. Items are
referenced by id, the user is a system-wide unique string and the tags is a
simple list of strings.

Before updating the engine we need to ensure that persistent objects can be
adapted to key references:

  >>> import zope.component
  >>> from zope.app.keyreference import testing

  >>> zope.component.provideAdapter(testing.SimpleKeyReference)


Instead providing a separate API for adding and updating tags, both actions
are done via the ``update()`` method. Think of it as updating the tagging
engine.

  >>> engine.update(1, u'srichter', [u'USA', u'personal'])
  >>> engine.update(2, u'srichter', [u'austria', u'lovely'])
  >>> engine.update(3, u'jodok', [u'Austria', u'personal'])
  >>> engine.update(2, u'jodok', [u'austria', u'lovely', u'work'])

Next you can ask the engine several questions.

Querying for Tags
~~~~~~~~~~~~~~~~~

A common request is to ask for tags based on items and users. First, you can
ask for all tags for a particular item:

  >>> sorted(engine.getTags(items=(1,)))
  [u'USA', u'personal']

Note: The query methods return sets.

  >>> type(engine.getTags())
  <type 'set'>

The method always returns the normalized tag strings. You can also specify
several items:

  >>> sorted(engine.getTags(items=(1, 2)))
  [u'USA', u'austria', u'lovely', u'personal', u'work']

You can also ask for tags of a user:

  >>> sorted(engine.getTags(users=(u'srichter',)))
  [u'USA', u'austria', u'lovely', u'personal']

Again, you can specify multiple users:

  >>> sorted(engine.getTags(users=(u'srichter', u'jodok')))
  [u'Austria', u'USA', u'austria', u'lovely', u'personal', u'work']

Finally, you can also specify a combination of both:

  >>> sorted(engine.getTags(items=(1,), users=(u'srichter',)))
  [u'USA', u'personal']
  >>> sorted(engine.getTags(items=(3,), users=(u'srichter',)))
  []

You can also query all tags by not specifying items or users:

  >>> sorted(engine.getTags())
  [u'Austria', u'USA', u'austria', u'lovely', u'personal', u'work']


Querying for Items
~~~~~~~~~~~~~~~~~~

This method allows to look for items. For example, we would like to find all
items that have the "personal" tag:

  >>> sorted(engine.getItems(tags=(u'personal',)))
  [1, 3]

Note: The query methods return sets.

  >>> type(engine.getItems())
  <type 'set'>

Furthermore, you can query for all items of a particular user:

  >>> sorted(engine.getItems(users=(u'srichter',)))
  [1, 2]
  >>> sorted(engine.getItems(users=(u'srichter', u'jodok')))
  [1, 2, 3]

Finally, you can combine tag and user specifications:

  >>> sorted(engine.getItems(
  ...     tags=(u'personal',), users=(u'srichter', u'jodok')))
  [1, 3]

You can also query all items by not specifying tags or users:

  >>> sorted(engine.getItems())
  [1, 2, 3]


Querying for Users
~~~~~~~~~~~~~~~~~~

Similar to the two methods above, you can query for users. First we are
looking for all users specifying a particular tag.

  >>> sorted(engine.getUsers(tags=(u'personal',)))
  [u'jodok', u'srichter']
  >>> sorted(engine.getUsers(tags=(u'Austria',)))
  [u'jodok']

Note: The query methods return sets.

  >>> type(engine.getUsers())
  <type 'set'>

Next you can also find all items that that have been tagged by a user:

  >>> sorted(engine.getUsers(items=(1,)))
  [u'srichter']
  >>> sorted(engine.getUsers(items=(2,)))
  [u'jodok', u'srichter']

As before you can combine the two criteria as well:

  >>> sorted(engine.getUsers(tags=(u'USA',), items=(1,)))
  [u'srichter']
  >>> sorted(engine.getUsers(tags=(u'personal',), items=(1, 3)))
  [u'jodok', u'srichter']

You can also query all users by not specifying tags or items:

  >>> sorted(engine.getUsers())
  [u'jodok', u'srichter']


Combining Queries
-----------------

Since those query methods return sets, you can easily combine them:

  >>> users1 = engine.getUsers(items=(1,))
  >>> users2 = engine.getUsers(items=(2,))
  >>> sorted(users1.intersection(users2))
  [u'srichter']


Changing and deleting Entries
-----------------------------

"srichter" moved from USA to Germany:

  >>> engine.update(1, u'srichter', [u'Germany', u'personal'])
  >>> sorted(engine.getTags(items=(1,), users=(u'srichter',)))
  [u'Germany', u'personal']


We delete entries by passing an empty list to the update method:

  >>> engine.update(1, u'srichter', [])
  >>> sorted(engine.getTags(items=(1,)))
  []
  >>> sorted(engine.getTags())
  [u'Austria', u'austria', u'lovely', u'personal', u'work']
  >>> sorted(engine.getItems())
  [2, 3]

Now let's delete the tags of the second item. We want to be sure that
"srichter" can't be found anymore:

  >>> engine.update(2, u'srichter', [])
  >>> sorted(engine.getUsers())
  [u'jodok']


Tag Object
----------

Internally, the tagging engine uses the ``Tag`` class to store all data about
one particular item, user and tag names pair.

  >>> from lovely.tag.tag import Tag

The ``Tag`` object is initialized with the three pieces information mentioned
above.

  >>> sample = Tag(1, u'user', u'tag1')
  >>> sample
  <Tag u'tag1' for 1 by u'user'>

You can also think of those three items as the unique key of the
tag. Additionally to those three attributes, a creation date is also
specified:

  >>> sample.item
  1
  >>> sample.user
  u'user'
  >>> sample.name
  u'tag1'
  >>> sample.timestamp
  datetime.datetime(...)


Taggable Objects
----------------

Theoretically all objects are taggable. But this might not be desirable. Thus
objects must provide the ``ITaggable`` interface to be taggable.

  >>> import zope.interface

  >>> class Image(object):
  ...     zope.interface.implements(tag.interfaces.ITaggable)
  >>> image = Image()

  >>> class File(object):
  ...     pass
  >>> file = File()

Taggable objects can then be adapted to the ``ITagging`` interface. For this
to work we have to register the adapter:

  >>> zope.component.provideAdapter(tag.Tagging)

Before we can now use the tagging object, we need to register our tagging
engine as well as the integer id generator as a utility:

  >>> zope.component.provideUtility(engine, tag.interfaces.ITaggingEngine)

  >>> from zope.app import intid
  >>> zope.component.provideUtility(intid.IntIds(), intid.interfaces.IIntIds)

Adapting the file to be tagged should fail:

  >>> tag.interfaces.ITagging(file)
  Traceback (most recent call last):
  ...
  TypeError: ('Could not adapt', <File ...>, <InterfaceClass ...ITagging>)

But images can be tagged:

  >>> tagging = tag.interfaces.ITagging(image)

At first there are no tags for the image:

  >>> sorted(tagging.getTags())
  []

Let's now have "srichter" and "jodok" add a few tags:

  >>> tagging.update(u'srichter', [u'home', u'USA'])
  >>> tagging.update(u'jodok', [u'vacation', u'USA'])

  >>> sorted(tagging.getTags())
  [u'USA', u'home', u'vacation']

Of course, you can also ask just for the tags by "srichter":

  >>> sorted(tagging.getTags(users=[u'srichter']))
  [u'USA', u'home']

Further you can request to see all users that have tagged the image:

  >>> sorted(tagging.getUsers())
  [u'jodok', u'srichter']

or all users that have specified a particular tag:

  >>> sorted(tagging.getUsers(tags=(u'home',)))
  [u'srichter']
  >>> sorted(tagging.getUsers(tags=(u'USA',)))
  [u'jodok', u'srichter']

Using Named Tagging Engines
---------------------------

  >>> class INamedTagging(tag.interfaces.ITagging):
  ...     pass
  >>> class NamedTagging(tag.Tagging):
  ...     zope.interface.implements(INamedTagging)
  ...     zope.component.adapts(tag.interfaces.ITaggable)
  ...     engineName = 'IAmNamed'
  >>> zope.component.provideAdapter(NamedTagging,
  ...                               (tag.interfaces.ITaggable,),
  ...                               INamedTagging)

  >>> namedTagging = INamedTagging(image)
  >>> namedTagging.tags = ['named1', 'named2']
  >>> namedTagging.update(u'jukart', [u'works', u'hard'])
  Traceback (most recent call last):
  ...
  ComponentLookupError: (<InterfaceClass lovely.tag.interfaces.ITaggingEngine>, 'IAmNamed')

We have no named tagging engine registered yet. Let's see what happens if we
update with an empty list of tags.

  >>> namedTagging.update(u'jukart', [])

If we update without tags it is possible that we do this because an object has
been deleted. This is usually done in an event handler for ObjectRemovedEvent.
If we would raise an exeption in this case it is not possible to delete a site.

Now we register a named tagging engine.

  >>> namedEngine = tag.TaggingEngine()
  >>> zope.component.provideUtility(namedEngine, tag.interfaces.ITaggingEngine,
  ...                               name='IAmNamed')

  >>> namedTagging = INamedTagging(image)
  >>> namedTagging.tags = ['named1', 'named2']
  >>> sorted(namedTagging.getTags())
  []
  >>> namedTagging.update(u'jukart', [u'works', u'hard'])
  >>> sorted(namedTagging.getTags())
  [u'hard', u'works']

The new tags are not in the unnamed tagging engine.

  >>> sorted(tagging.getTags())
  [u'USA', u'home', u'vacation']


IUserTagging
------------

There is also an adapter for ITaggable objects which provides a simple
tag attribute which accepts a list of tags defined for the ITaggable
by the current principal.

  >>> zope.component.provideAdapter(tag.UserTagging)
  >>> userTagging = tag.interfaces.IUserTagging(image)
  >>> userTagging.tags
  Traceback (most recent call last):
  ...
  ValueError: User not found

We get a ValueError because we have no interaction in this test, and
therefore the implementation cannot find the principal. We have to
create a principal and a participation.

  >>> from zope.security.testing import Principal, Participation
  >>> from zope.security import management
  >>> p = Principal(u'srichter')
  >>> participation = Participation(p)
  >>> management.endInteraction()
  >>> management.newInteraction(participation)
  >>> sorted(userTagging.tags)
  [u'USA', u'home']
  >>> userTagging.tags = [u'zope3', u'guru']
  >>> sorted(userTagging.tags)
  [u'guru', u'zope3']

Tag Clouds
----------

All portals like Flickr, del.icio.us use tagging and generate tag clouds.
Tag clouds contain tags and their frequency.

The ``getCloud`` method returns a set of tuples in the form of 
('tag', frequency). 

  >>> type(engine.getCloud())
  <type 'set'>

Now let's add some tags to generate clouds later:

  >>> engine.update(3, u'michael', [u'Austria', u'Bizau'])
  >>> engine.update(2, u'michael', [u'lovely', u'USA'])
  >>> engine.update(1, u'jodok', [u'USA',])

The most common use-case is to generate a global tag cloud.

  >>> sorted(engine.getCloud())
  [(u'Austria', 2), (u'Bizau', 1), (u'USA', 3), (u'austria', 1),
   (u'guru', 1), (u'lovely', 2), (u'personal', 1), (u'vacation', 1),
   (u'work', 1), (u'zope3', 1)]

Of course you can generate clouds on item basis. You can't pass a tuple of
items, only a single one is allowed:

  >>> sorted(engine.getCloud(item=1))
  [(u'USA', 1)]
  
The same applies to queries by user:

  >>> sorted(engine.getCloud(user=u'srichter'))
  [(u'guru', 1), (u'zope3', 1)]
  
It makes no sense to combine user and item. This will never be a cloud.

  >>> engine.getCloud(item=1, user=u'srichter')
  Traceback (most recent call last):
  ...
  ValueError: You cannot specify both, an item and an user.


Related Tags
------------

An advanced feature of the tagging engine is to find all tags that are related
to a given tag.

  >>> sorted(engine.getRelatedTags(u'austria'))
  [u'lovely', u'work']

By default the method only searches for the first degree related tags. You can
also search for other degrees:

  >>> engine.update(4, u'jodok', [u'lovely', u'dornbirn', u'personal'])
  >>> sorted(engine.getRelatedTags(u'austria', degree=2))
  [u'USA', u'dornbirn', u'lovely', u'personal', u'work']

  >>> engine.update(4, u'jodok', [u'lovely', u'dornbirn', u'personal'])
  >>> sorted(engine.getRelatedTags(u'austria', degree=3))
  [u'Austria', u'USA', u'dornbirn', u'lovely', u'personal',
   u'vacation', u'work']

Frequency Of Tags
-----------------

If we have a list of tags we can ask for the frequencies of the tags.

  >>> sorted(engine.getFrequency([u'Austria', u'USA']))
  [(u'Austria', 2), (u'USA', 3)]

We get a frequency of 0 if we ask for a tag which is not in the engine.

  >>> sorted(engine.getFrequency([u'Austria', u'jukart', u'USA']))
  [(u'Austria', 2), (u'USA', 3), (u'jukart', 0)]


