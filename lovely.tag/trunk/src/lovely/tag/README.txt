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
referenced by their intId, the user is a system-wide unique string and
the tags is a simple list of strings.

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
  >>> sorted(engine.getTags(items=(1, 2), users=(u'srichter',)))
  [u'USA', u'austria', u'lovely', u'personal']
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


Querying for Tagobjects
~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it is usefull to have the actual tag objects directly. These
tag objects can be queried by tagnames, users and items.

  >>> sorted(engine.getTagObjects(tags=(u'personal',)))
  [<Tag u'personal' for 1 by u'srichter'>,
   <Tag u'personal' for 3 by u'jodok'>]
  >>> sorted(engine.getTagObjects(tags=(u'personal',),
  ...                             users=(u'srichter',)))
  [<Tag u'personal' for 1 by u'srichter'>]
  >>> sorted(engine.getTagObjects(tags=(u'personal',),
  ...                             items=(3,)))
  [<Tag u'personal' for 3 by u'jodok'>]

We can also search fr

Tagging Statistics
------------------

  >>> from lovely.tag.interfaces import ITaggingStatistics
  >>> ITaggingStatistics.providedBy(engine)
  True
  >>> engine.tagCount
  6
  >>> engine.itemCount
  3
  >>> engine.userCount
  2


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

In order to delete entries globaly use the delete method described below.

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
  >>> intIds = intid.IntIds()
  >>> zope.component.provideUtility(intIds, intid.interfaces.IIntIds)

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
('tag', frequency). It takes the same arguments as getTags.

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

  >>> sorted(engine.getCloud(items=[1]))
  [(u'USA', 1)]

The same applies to queries by user:

  >>> sorted(engine.getCloud(users=[u'srichter']))
  [(u'guru', 1), (u'zope3', 1)]

Or more users, and a few items.

  >>> sorted(engine.getCloud(items=[1, 2, 3], users=[u'srichter', u'jodok']))
  [(u'Austria', 1), (u'USA', 1), (u'austria', 1),
   (u'lovely', 1), (u'personal', 1), (u'work', 1)]

Re-updating tags for same user does not affect cloud weight

   >>> engine.update(1, u'jodok', [u'USA',])
   >>> sorted(engine.getCloud(items=[1, 2, 3], users=[u'srichter', u'jodok']))
   [(u'Austria', 1), (u'USA', 1), (u'austria', 1),
   (u'lovely', 1), (u'personal', 1), (u'work', 1)]


Re-updating tags for same user does not affect cloud weight

  >>> engine.update(1, u'jodok', [u'USA',])
  >>> sorted(engine.getCloud(items=[1, 2, 3], users=[u'srichter', u'jodok']))
  [(u'Austria', 1), (u'USA', 1), (u'austria', 1),
   (u'lovely', 1), (u'personal', 1), (u'work', 1)]


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


Related Items
-------------

Another advanced feature is to provide related items.

We set up a new engine for this test. Items are related if they have at least
one tag in common.

  >>> relatedEngine = tag.TaggingEngine()
  >>> relatedEngine.update(1, u'srichter', [u'USA', u'personal', u'zope'])
  >>> relatedEngine.update(2, u'srichter', [u'austria', u'lovely'])
  >>> relatedEngine.update(3, u'jodok', [u'Austria', u'personal'])
  >>> relatedEngine.update(2, u'jodok', [u'austria', u'lovely', u'work'])
  >>> relatedEngine.update(4, u'jukart', [u'austria', u'Austria', u'lovely', u'work'])
  >>> relatedEngine.update(5, u'jim', [u'USA', u'zope'])

We get tuples with the related item and the number of tags in common.

  >>> relatedEngine.getRelatedItems(1)
  [(5, 2), (3, 1)]
  >>> relatedEngine.getRelatedItems(5)
  [(1, 2)]
  >>> relatedEngine.getRelatedItems(2)
  [(4, 3)]


Related Users
-------------

We can also get related users. Users are related if they have at least one tag
in common.

  >>> relatedEngine.getRelatedUsers(u'jim')
  [(u'srichter', 2)]
  >>> relatedEngine.getRelatedUsers(u'jodok')
  [(u'jukart', 4), (u'srichter', 3)]


Frequency Of Tags
-----------------

If we have a list of tags we can ask for the frequencies of the tags.

  >>> sorted(engine.getFrequency([u'Austria', u'USA']))
  [(u'Austria', 2), (u'USA', 3)]

We get a frequency of 0 if we ask for a tag which is not in the engine.

  >>> sorted(engine.getFrequency([u'Austria', u'jukart', u'USA']))
  [(u'Austria', 2), (u'USA', 3), (u'jukart', 0)]


Removal of Tag objects
----------------------


When an object is unregistered from the intids utility it will be
removed from each engine. Let us see how much items we have so far.

  >>> len(engine.getItems())
  5
  >>> len(namedEngine.getItems())
  1

We can use the delete method of the tagging engine to delete tag
objects by defining the user, item or a tag name.

  >>> u'austria' in engine.getTags()
  True
  >>> engine.delete(tag=u'austria')
  >>> u'austria' in engine.getTags()
  False

If we delete tags for a user, the tags still exists for other users.

  >>> sorted(engine.getTags(users=(u'jodok',)))
  [u'Austria', u'USA', u'dornbirn', u'lovely',
   u'personal', u'vacation', u'work']
  >>> engine.delete(user=u'jodok')
  >>> sorted(engine.getTags(users=(u'jodok',)))
  []
  >>> sorted(engine.getTags())
  [u'Austria', u'Bizau', u'USA', u'guru', u'lovely', u'zope3']

This is also possible with items.

  >>> sorted(engine.getTags(items=(3,)))
  [u'Austria', u'Bizau']

Let us add a tag tag from the item to another item to show the behaviour.

  >>> engine.update(2, u'srichter', [u'Austria'])
  >>> engine.delete(item=3)
  >>> sorted(engine.getTags(items=(3,)))
  []

The 'Austria' tag is still there.

  >>> sorted(engine.getTags())
  [u'Austria', u'USA', u'guru', u'lovely', u'zope3']

Let us setup the handler and events.

  >>> from zope.component import eventtesting
  >>> from zope import event
  >>> from lovely.tag.engine import removeItemSubscriber
  >>> from zope.app.intid.interfaces import IntIdRemovedEvent
  >>> from zope.app.intid import removeIntIdSubscriber
  >>> zope.component.provideHandler(removeItemSubscriber)

If we now fire the intid remove event with our image object, it should
get removed in both engines.

  >>> len(namedEngine.getItems())
  1
  >>> len(engine.getItems())
  2
  >>> removeIntIdSubscriber(image, None)
  >>> len(namedEngine.getItems())
  0
  >>> len(engine.getItems())
  1


Removing Stale Items
--------------------

You can remove stale items from the tagging engine. Stale means that
the item is not available anymore by the intids utility.

Because we removed any objects with intids before, we have an empty
intid utility.

  >>> sorted(intIds.refs.keys())
  []

But above we defined an item with an id that does not exist. So this
is a stale item.

  >>> sorted(engine.getItems())
  [2]

Let us add our image object again.

  >>> tagging = tag.interfaces.ITagging(image)
  >>> tagging.update(u'srichter', [u'newtag'])

This is our first and only entry in the intid util

   >>> intIds.refs.keys()[0] in engine.getItems()
   True

Our stale entry is 2. The intids of the items deleted are returned.

   >>> 2  in engine.getItems()
   True
   >>> engine.cleanStaleItems()
   [2]

We now only have our real image item.

   >>> 2  in engine.getItems()
   False
   >>> len(engine.getItems())
   1
   >>> sorted(engine.getItems())[0] == intIds.refs.keys()[0]
   True


Renaming Tags
-------------

It is also possible to rename tags globally in the engine.

   >>> tagging.update(u'srichter', [u'tagtorename', u'usa'])
   >>> tagging.update(u'jukart', [
   ...     u'tagtorename', u'someothertag', u'renamedtag'])
   >>> engine.update(123, 'jukart', [u'tagtorename'])
   >>> sorted(engine.getTags())
   [u'renamedtag', u'someothertag', u'tagtorename', u'usa']
   >>> sorted(engine.getTags(users=[u'jukart']))
   [u'renamedtag', u'someothertag', u'tagtorename']
   >>> len(sorted(engine.getItems(tags=[u'tagtorename'])))
   2
   >>> len(sorted(engine.getItems(tags=[u'renamedtag'])))
   1
   >>> sorted(engine.getTags(users=[u'srichter']))
   [u'tagtorename', u'usa']

The rename method returns the number of renamed tag objects.

   >>> engine.rename(u'tagtorename', u'renamedtag')
   3
   >>> sorted(engine.getTags())
   [u'renamedtag', u'someothertag', u'usa']

Tags are joined if the new name already exists.

   >>> sorted(engine.getTags(users=[u'jukart']))
   [u'renamedtag', u'someothertag']
   >>> sorted(engine.getTags(users=[u'srichter']))
   [u'renamedtag', u'usa']
   >>> len(sorted(engine.getItems(tags=[u'tagtorename'])))
   0
   >>> len(sorted(engine.getItems(tags=[u'renamedtag'])))
   2

Normalizing Tags
----------------

It is also possible to normalize tags with a callable ojbect which
returns a new name for any given name.
lower case.

   >>> engine.update(123, 'jukart', [u'RenamedTag', u'USA'])
   >>> sorted(engine.getTags())
   [u'RenamedTag', u'USA', u'renamedtag', u'someothertag', u'usa']

Let us normalize all tags to lowercase by using the lower function
from the string module.

   >>> import string

The normalize method returns the number of tag objects affected.

   >>> engine.normalize(string.lower)
   2
   >>> sorted(engine.getTags())
   [u'renamedtag', u'someothertag', u'usa']

The normalize method also accepts a python dotted name, which will be
resolved to a global object.

   >>> engine.normalize('string.upper')
   7
   >>> sorted(engine.getTags())
   [u'RENAMEDTAG', u'SOMEOTHERTAG', u'USA']
