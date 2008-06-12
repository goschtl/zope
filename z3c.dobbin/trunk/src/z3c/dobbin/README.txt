Developer documentation
=======================

Dobbin creates ORM mappers based on class specification. Columns are
infered from interface schema fields and attributes, and a class may
be provided as the mapper metatype.

Interface mapping
-----------------

An mapper adapter is provided.

   >>> from z3c.dobbin.mapper import getMapper
   >>> component.provideAdapter(getMapper)

We begin with a database session.

    >>> import ore.alchemist
    >>> session = ore.alchemist.Session()

Define a schema interface:

    >>> class IAlbum(interface.Interface):
    ...     artist = schema.TextLine(
    ...         title=u"Artist",
    ...         default=u"")
    ...
    ...     title = schema.TextLine(
    ...         title=u"Title",
    ...         default=u"")

We can then fabricate an instance that implements this interface by
using the ``create`` method.

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
    
    >>> import transaction
    >>> transaction.commit()

We get a reference to the database metadata object, to locate each
underlying table.
    
    >>> from ore.alchemist.interfaces import IDatabaseEngine
    >>> engine = component.getUtility(IDatabaseEngine)
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
    >>> __builtin__.Vinyl = Vinyl

Create an instance using the ``create`` factory.
    
    >>> vinyl = create(Vinyl)

Verify that we've instantiated and instance of our class.
    
    >>> isinstance(vinyl, Vinyl)
    True

Copy the attributes from the Diana Ross vinyl record.

    >>> diana = session.query(IVinyl.__mapper__).select_by(
    ...     IAlbum.__mapper__.c.id==2)[0]

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

    >>> mapper = getMapper(Vinyl)
    >>> instance = mapper()
    >>> instance.uuid is not None
    True
    
Relations
---------

Most people have a favourite record.

    >>> class IFavorite(interface.Interface):
    ...     item = schema.Object(title=u"Item", schema=IVinyl)

Let's make our Diana Ross record a favorite.

    >>> favorite = create(IFavorite)
    >>> favorite.item = vinyl
    >>> favorite.item
    <Vinyl Diana Ross and The Supremes: Taking Care of Business (@ 45 RPM)>

    >>> session.save(favorite)
    
Get back the object.
    
    >>> favorite = session.query(IFavorite.__mapper__).select_by(
    ...     IFavorite.__mapper__.c.spec==IFavorite.__mapper__.__spec__)[0]

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

Internally, this is done by setting an attribute on the original
object that points to the database item, and maintaining a list of
pending objects on the current database session:

    >>> cleaner._d_uuid in session._d_pending
    True

However, once we commit the transaction, the relation is no longer
attached to the relation source, and the correct data will be
persisted in the database.

    >>> cleaner.name = u"CD cleaner"
    >>> transaction.commit()
    >>> favorite.item.name
    u'CD cleaner'
    
This behavior should work well in a request-response type environment,
where the request will typically end with a commit.

Collections
-----------

Let's set up a record collection as a list.

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

    >>> from z3c.dobbin.relations import lookup
    >>> collection = lookup(collection.uuid)

Let's verify that we've stored the Diana Ross record.
    
    >>> record = collection.records[0]
    
    >>> record.artist, record.title
    (u'Diana Ross and The Supremes', u'Taking Care of Business')

    >>> transaction.commit()
    
When we create a new, transient object and append it to a list, it's
automatically saved on the session.

    >>> collection = lookup(collection.uuid)

    >>> vinyl = create(IVinyl)
    >>> vinyl.artist = u"Kool & the Gang"
    >>> vinyl.album = u"Music Is the Message"
    >>> vinyl.rpm = 33

    >>> collection.records.append(vinyl)
    >>> [record.artist for record in collection.records]
    [u'Diana Ross and The Supremes', u'Kool & the Gang']

    >>> transaction.commit()
    >>> session.update(collection)
    
We can remove items.

    >>> collection.records.remove(vinyl)
    >>> len(collection.records) == 1
    True

And extend.

    >>> collection.records.extend((vinyl,))
    >>> len(collection.records) == 2
    True

Items can appear twice in the list.

    >>> collection.records.append(vinyl)
    >>> len(collection.records) == 3
    True

We can add concrete instances to collections.

    >>> vinyl = Vinyl()
    >>> collection.records.append(vinyl)
    >>> len(collection.records) == 4
    True

And remove them, too.

    >>> collection.records.remove(vinyl)
    >>> len(collection.records) == 3
    True

For good measure, let's create a new instance without adding any
elements to its list.

    >>> _ = create(ICollection)

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
    >>> '__name__' in mapper.c
    False

Cleanup
-------
    
Commit session.
    
    >>> transaction.commit()
