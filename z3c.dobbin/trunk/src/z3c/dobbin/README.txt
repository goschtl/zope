Walk-through of the framework
=============================

This section demonstrates the main functionality of the package using
the doctest format. 

We begin with a new database session.

    >>> import z3c.saconfig
    >>> session = z3c.saconfig.Session()

Mappers from interface specification
------------------------------------

We'll start out creating mappers directly from an interface
specification. The instances will only afford access to the declared
attributes and have no methods.

We start out with an interface decribing a recorded album.

    >>> class IAlbum(interface.Interface):
    ...     artist = schema.TextLine(
    ...         title=u"Artist",
    ...         default=u"")
    ...
    ...     title = schema.TextLine(
    ...         title=u"Title",
    ...         default=u"")

We can now fabricate instances that implement this interface by using
the ``create`` method. This is a shorthand for setting up the mapper
and creating an instance using its factory.

    >>> from z3c.dobbin.factory import create
    >>> album = create(IAlbum)

Set attributes.
    
    >>> album.artist = "The Beach Boys"
    >>> album.title = u"Pet Sounds"
    
Interface inheritance is supported. For instance, a vinyl record is a
particular type of album.

    >>> class IVinyl(IAlbum):
    ...     rpm = schema.Int(
    ...         title=u"RPM",
    ...         default=33)

    >>> vinyl = create(IVinyl)

What actually happens on the database side is that columns are mapped
to the interface that they provide.

Let's demonstrate that the mapper instance actually implements the
defined fields.

    >>> vinyl.artist = "Diana Ross and The Supremes"
    >>> vinyl.title = "Taking Care of Business"
    >>> vinyl.rpm = 45

Or a compact disc.

    >>> class ICompactDisc(IAlbum):
    ...     year = schema.Int(title=u"Year")

    >>> cd = create(ICompactDisc)

Let's pick a more recent Diana Ross, to fit the format.
    
    >>> cd.artist = "Diana Ross"
    >>> cd.title = "The Great American Songbook"
    >>> cd.year = 2005
    
To verify that we've actually inserted objects to the database, we
commit the transacation, thus flushing the current session.

    >>> session.save(album)
    >>> session.save(vinyl)
    >>> session.save(cd)

We must actually query the database once before proceeding; this seems
to be a bug in ``zope.sqlalchemy``.
    
    >>> results = session.query(album.__class__).all()
    
    >>> import transaction
    >>> transaction.commit()

We get a reference to the database metadata object, to locate each
underlying table.
    
    >>> engine = session.bind
    >>> metadata = engine.metadata

Tables are given a name based on the dotted path of the interface they
describe. A utility method is provided to create a proper table name
for an interface.
    
    >>> from z3c.dobbin.mapper import encode

Verify tables for ``IVinyl``, ``IAlbum`` and ``ICompactDisc``.
    
    >>> session.bind = metadata.bind
    >>> session.execute(metadata.tables[encode(IVinyl)].select()).fetchall()
    [(2, 45)]

    >>> session.execute(metadata.tables[encode(IAlbum)].select()).fetchall()
    [(1, u'Pet Sounds', u'The Beach Boys'),
     (2, u'Taking Care of Business', u'Diana Ross and The Supremes'),
     (3, u'The Great American Songbook', u'Diana Ross')]

    >>> session.execute(metadata.tables[encode(ICompactDisc)].select()).fetchall()
    [(3, 2005)]

Concrete class specification
----------------------------
    
Now we'll create a mapper based on a concrete class. We'll let the
class implement the interface that describes the attributes we want to
store, but also provides a custom method.

    >>> class Vinyl(object):
    ...     interface.implements(IVinyl)
    ...
    ...     artist = title = u""
    ...     rpm = 33
    ...
    ...     def __repr__(self):
    ...         return "<Vinyl %s: %s (@ %d RPM)>" % \
    ...                (self.artist, self.title, self.rpm)

Although the symbols we define in this test report that they're
available from the ``__builtin__`` module, they really aren't.

We'll manually add these symbols.

    >>> import __builtin__
    >>> __builtin__.IVinyl = IVinyl
    >>> __builtin__.IAlbum = IAlbum
    >>> __builtin__.Vinyl = Vinyl

Create an instance using the ``create`` factory.
    
    >>> vinyl = create(Vinyl)

Verify that we've instantiated and instance of our class.
    
    >>> isinstance(vinyl, Vinyl)
    True

Copy the attributes from the Diana Ross vinyl record.

    >>> diana = session.query(IVinyl.__mapper__).filter_by(
    ...     artist=u"Diana Ross and The Supremes")[0]
    >>> vinyl.artist = diana.artist
    >>> vinyl.title = diana.title
    >>> vinyl.rpm = diana.rpm

Verify that the methods on our ``Vinyl``-class are available on the mapper.

    >>> repr(vinyl)
    '<Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>'

If we're mapping a concrete class, and run into class properties, we
won't instrument them even if they're declared by the schema.

    >>> class Experimental(Vinyl):
    ...     @property
    ...     def rpm(self):
    ...         return len(self.title+self.artist)

    >>> experimental = create(Experimental)
    >>> experimental.artist = vinyl.artist
    >>> experimental.title = vinyl.title

Let's see how fast this record should be played back.

    >>> experimental.rpm
    50

Instances of mappers automatically join the object soup.

    >>> from z3c.dobbin.mapper import getMapper
    >>> mapper = getMapper(Vinyl)
    >>> instance = mapper()
    >>> instance.uuid is not None
    True
    
Relations
---------

Relations are columns that act as references to other objects.

As an example, let's create an object holds a reference to some
favorite item. We use ``zope.schema.Object`` to declare this
reference; relations are polymorphic and we needn't declare the schema
of the referenced object in advance.

    >>> class IFavorite(interface.Interface):
    ...     item = schema.Object(title=u"Item", schema=interface.Interface)

    >>> __builtin__.IFavorite = IFavorite
    
Let's make our Diana Ross record a favorite.

    >>> favorite = create(IFavorite)
    >>> favorite.item = vinyl
    >>> favorite.item
    <Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>

    >>> session.save(favorite)

We'll commit the transaction and lookup the object by its UUID.

    >>> transaction.commit()

    >>> from z3c.dobbin.soup import lookup
    >>> favorite = lookup(favorite.uuid)
    
When we retrieve the related items, it's automatically reconstructed
to match the specification to which it was associated.

    >>> favorite.item
    <Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>

We can create relations to objects that are not mapped. Let's model an
accessory item.

    >>> class IAccessory(interface.Interface):
    ...     name = schema.TextLine(title=u"Name of accessory")

    >>> class Accessory(object):
    ...     interface.implements(IAccessory)
    ...
    ...     def __repr__(self):
    ...          return "<Accessory '%s'>" % self.name

If we now instantiate an accessory and assign it as a favorite item,
we'll implicitly create a mapper from the class specification and
insert it into the database.

    >>> cleaner = Accessory()
    >>> cleaner.name = u"Record cleaner"

Set up relation.
    
    >>> favorite.item = cleaner       

Let's try and get back our record cleaner item.

    >>> __builtin__.Accessory = Accessory
    >>> favorite.item
    <Accessory 'Record cleaner'>

Within the same transaction, the relation will return the original
object, maintaining integrity.

    >>> favorite.item is cleaner
    True

The session keeps a copy of the pending object until the transaction
is ended.

    >>> cleaner in session._d_pending.values()
    True

However, once we commit the transaction, the relation is no longer
attached to the relation source, and the correct data will be
persisted in the database.

    >>> cleaner.name = u"CD cleaner"
    
    >>> session.flush()
    >>> session.update(favorite)
    
    >>> favorite.item.name
    u'CD cleaner'
    
This behavior should work well in a request-response type environment,
where the request will typically end with a commit.

Collections
-----------

We can instrument properties that behave like collections by using the
sequence and mapping schema fields.

Let's set up a record collection as an ordered list.

    >>> class ICollection(interface.Interface):
    ...     records = schema.List(
    ...         title=u"Records",
    ...         value_type=schema.Object(schema=IAlbum)
    ...         )

    >>> __builtin__.ICollection = ICollection
    
    >>> collection = create(ICollection)
    >>> collection.records
    []

Add the Diana Ross record, and save the collection to the session.

    >>> collection.records.append(diana)
    >>> session.save(collection)
    
We can get our collection back.

    >>> collection = lookup(collection.uuid)

Let's verify that we've stored the Diana Ross record.
    
    >>> record = collection.records[0]
    
    >>> record.artist, record.title
    (u'Diana Ross and The Supremes', u'Taking Care of Business')

    >>> session.flush()
    
When we create a new, transient object and append it to a list, it's
automatically saved on the session.

    >>> collection = lookup(collection.uuid)

    >>> kool = create(IVinyl)
    >>> kool.artist = u"Kool & the Gang"
    >>> kool.title = u"Music Is the Message"
    >>> kool.rpm = 33
    
    >>> collection.records.append(kool)
    >>> [record.artist for record in collection.records]
    [u'Diana Ross and The Supremes', u'Kool & the Gang']

    >>> session.flush()
    >>> session.update(collection)

We can remove items.

    >>> collection.records.remove(kool)
    >>> len(collection.records) == 1
    True

And extend.

    >>> collection.records.extend((kool,))
    >>> len(collection.records) == 2
    True

Items can appear twice in the list.

    >>> collection.records.append(kool)
    >>> len(collection.records) == 3
    True

We can add concrete instances to collections.

    >>> marvin = Vinyl()
    >>> marvin.artist = u"Marvin Gaye"
    >>> marvin.title = u"Let's get it on"
    >>> marvin.rpm = 33
    
    >>> collection.records.append(marvin)
    >>> len(collection.records) == 4
    True

And remove them, too.

    >>> collection.records.remove(marvin)
    >>> len(collection.records) == 3
    True

The standard list methods are available.

    >>> collection.records = [marvin, vinyl]
    >>> collection.records.sort(key=lambda record: record.artist)
    >>> collection.records
    [<Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>,
     <Vinyl Marvin Gaye: Let's get it on (@ 33 RPM)>]

    >>> collection.records.reverse()
    >>> collection.records
    [<Vinyl Marvin Gaye: Let's get it on (@ 33 RPM)>,
     <Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>]

    >>> collection.records.index(vinyl)
    1
    
    >>> collection.records.pop()
    <Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>

    >>> collection.records.insert(0, vinyl)
    >>> collection.records
    [<Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>,
     <Vinyl Marvin Gaye: Let's get it on (@ 33 RPM)>]

    >>> collection.records.count(vinyl)
    1

    >>> collection.records[1] = vinyl
    >>> collection.records.count(vinyl)
    2
    
For good measure, let's create a new instance without adding any
elements to its list.

    >>> empty_collection = create(ICollection)
    >>> session.save(empty_collection)

To demonstrate the mapping implementation, let's set up a catalog for
our record collection. We'll index the records by their ASIN string.
    
    >>> class ICatalog(interface.Interface):
    ...     index = schema.Dict(
    ...         title=u"Record index")
    
    >>> catalog = create(ICatalog)
    >>> session.save(catalog)

Add a record to the index.
    
    >>> catalog.index[u"B00004WZ5Z"] = diana
    >>> catalog.index[u"B00004WZ5Z"]
    <Mapper (__builtin__.IVinyl) at ...>

Verify state after commit.
    
    >>> transaction.commit()
    >>> catalog.index[u"B00004WZ5Z"]
    <Mapper (__builtin__.IVinyl) at ...>

Let's check that the standard dict methods are supported.

    >>> catalog.index.values()
    [<Mapper (__builtin__.IVinyl) at ...>]

    >>> tuple(catalog.index.itervalues())
    (<Mapper (__builtin__.IVinyl) at ...>,)

    >>> catalog.index.setdefault(u"B00004WZ5Z", None)
    <Mapper (__builtin__.IVinyl) at ...>

    >>> catalog.index.pop(u"B00004WZ5Z")
    <Mapper (__builtin__.IVinyl) at ...>

    >>> len(catalog.index)
    0

Concrete instances are supported.

    >>> vinyl = Vinyl()
    >>> vinyl.artist = diana.artist
    >>> vinyl.title = diana.title
    >>> vinyl.rpm = diana.rpm

    >>> catalog.index[u"B00004WZ5Z"] = vinyl
    >>> len(catalog.index)
    1

    >>> catalog.index.popitem()
    (u'B00004WZ5Z',
     <Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>)

    >>> catalog.index = {u"B00004WZ5Z": vinyl}
    >>> len(catalog.index)
    1

    >>> catalog.index.clear()
    >>> len(catalog.index)
    0

We may use a mapped object as index.

    >>> catalog.index[diana] = diana
    >>> catalog.index.keys()[0] == diana.uuid
    True

    >>> transaction.commit()
    
    >>> catalog.index[diana]    
    <Mapper (__builtin__.IVinyl) at ...>
    
    >>> class IDiscography(ICatalog):
    ...     records = schema.Dict(
    ...         title=u"Discographies by artist",
    ...         value_type=schema.List())

Polymorphic structures
----------------------

We can use weak typing to store (almost) any kind of structure. Values
are kept as Python pickles.

    >>> class IPolyFavorite(interface.Interface):
    ...     item = interface.Attribute(u"Any kind of favorite")

    >>> __builtin__.IPolyFavorite = IPolyFavorite
    >>> favorite = create(IPolyFavorite)

A transaction hook makes sure that assigned values are transient
during a session.
    
    >>> obj = object()
    >>> favorite.item = obj
    >>> favorite.item is obj
    True
    
Integers, floats and unicode strings are straight-forward.
    
    >>> favorite.item = 42; transaction.commit()
    >>> favorite.item
    42

    >>> favorite.item = 42.01; transaction.commit()
    >>> 42 < favorite.item <= 42.01
    True

    >>> favorite.item = u"My favorite number is 42."; transaction.commit()
    >>> favorite.item
    u'My favorite number is 42.'

Normal strings need explicit coercing to ``str``.
    
    >>> favorite.item = "My favorite number is 42."; transaction.commit()
    >>> str(favorite.item)
    'My favorite number is 42.'

Or sequences of items.

    >>> favorite.item = (u"green", u"blue", u"red"); transaction.commit()
    >>> favorite.item
    (u'green', u'blue', u'red')

Dictionaries.

    >>> favorite.item = {u"green": 0x00FF00, u"blue": 0x0000FF, u"red": 0xFF0000}
    >>> transaction.commit()
    >>> favorite.item
    {u'blue': 255, u'green': 65280, u'red': 16711680}

    >>> favorite.item[u"black"] = 0x000000
    >>> sorted(favorite.item.items())
    [(u'black', 0), (u'blue', 255), (u'green', 65280), (u'red', 16711680)]

We do need explicitly set the dirty bit of this instance.

    >>> favorite.item = favorite.item
    >>> transaction.commit()

Clear the object cache and verify value.
    
    >>> del favorite._v_cached_item_pickle
    >>> sorted(favorite.item.items())
    [(u'black', 0), (u'blue', 255), (u'green', 65280), (u'red', 16711680)]
    
When we create relations to mutable objects, a hook is made into the
transaction machinery to keep track of the pending state.

    >>> some_list = [u"green", u"blue"]
    >>> favorite.item = some_list
    >>> some_list.append(u"red"); transaction.commit()
    >>> favorite.item
    [u'green', u'blue', u'red']

Amorphic structures.

    >>> favorite.item = ((1, u"green"), (2, u"blue"), (3, u"red")); transaction.commit()
    >>> favorite.item
    ((1, u'green'), (2, u'blue'), (3, u'red'))

Structures involving relations to other instances.

    >>> favorite.item = vinyl; transaction.commit()
    >>> del favorite._v_cached_item_pickle
    >>> favorite.item
    <Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>

Self-referencing works because polymorphic attributes are lazy.

    >>> session.save(favorite)
    
    >>> favorite.item = favorite; transaction.commit()
    >>> del favorite._v_cached_item_pickle
    >>> favorite.item
    <Mapper (__builtin__.IPolyFavorite) at ...>
    
Security
--------

The security model from Zope is applied to mappers.

    >>> from zope.security.checker import getCheckerForInstancesOf

Our ``Vinyl`` class does not have a security checker defined.
    
    >>> mapper = getMapper(Vinyl)
    >>> getCheckerForInstancesOf(mapper) is None
    True

Let's set a checker and regenerate the mapper.

    >>> from zope.security.checker import defineChecker, CheckerPublic
    >>> defineChecker(Vinyl, CheckerPublic)
    
    >>> from z3c.dobbin.mapper import createMapper
    >>> mapper = createMapper(Vinyl)
    >>> getCheckerForInstancesOf(mapper) is CheckerPublic
    True    
    
Known limitations
-----------------

Certain names are disallowed, and will be ignored when constructing
the mapper.

    >>> class IKnownLimitations(interface.Interface):
    ...     __name__ = schema.TextLine()

    >>> from z3c.dobbin.interfaces import IMapper
    >>> mapper = IMapper(IKnownLimitations)
    >>> mapper.__name__
    'Mapper'

Cleanup
-------
    
Commit session.
    
    >>> transaction.commit()
