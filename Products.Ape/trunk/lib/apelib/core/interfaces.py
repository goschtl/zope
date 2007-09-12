##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Public interfaces and exception classes.

$Id$
"""

from Interface import Interface, Attribute


class MappingError(Exception):
    """Object mapping exception"""

class SerializationError(MappingError):
    """Error during serialization"""

class DeserializationError(MappingError):
    """Error during deserialization"""

class StoreError(MappingError):
    """Error while storing"""

class LoadError(MappingError):
    """Error while loading"""

class ClassificationError(MappingError):
    """Error during classification"""

class ConfigurationError(Exception):
    """Invalid mapper configuration"""

class OIDConflictError(Exception):
    """Attempt to write an object with an OID already in use"""


class IClassFactory(Interface):
    """Class finder."""

    def get_class(module_name, class_name):
        """Returns the named class.

        A default implementation may use the Python's standard import
        mechanism.
        """


class IObjectDatabase (IClassFactory):
    """A collection of objects identifiable by OID.

    In apelib.zodb3, the ZODB Connection object (the _p_jar) is
    an IObjectDatabase.
    """

    def get(oid, classification=None):
        """Returns a class instance, possibly ghosted.

        Used during deserialization (loading/import).
        The classification argument, a mapping, may be provided as an
        optimization.  Without it, implementations of this method may
        have to load a full object rather than a ghosted object.
        """

    def identify(obj):
        """Returns the OID of an object.

        Used during serialization (storing/export).
        Returns None if the object is not in the object database.
        Raises TypeError if the object can not be stored directly
        in the database.
        """

    def new_oid():
        """Returns a new OID.

        Used during serialization (storing/export).
        """



class IDatabaseInitializer (Interface):
    """Provides a way to initialize a database."""

    def init(event):
        """Initializes the database, creating tables etc.

        event is an IDatabaseInitEvent.
        """


class IDatabaseInitEvent (Interface):
    """Interface for events involved in initializing databases."""

    connections = Attribute("connections", "A mapping of database connections")

    clear_all = Attribute("clear_all", """True to clear the database.

    This attribute is designed for testing purposes.
    """)


class IMapperEvent (Interface):
    """The base interface for events occurring in context of a mapper."""

    conf = Attribute("conf", "The IMapperConfiguration")

    mapper = Attribute("mapper", "The IMapper")

    oid = Attribute("oid", "The OID of the object being mapped")

    classification = Attribute(
        "classification", "The classification of the object.")


class IGatewayEvent (IMapperEvent):
    """Interface for events used by gateways."""

    connections = Attribute(
        "connections", "A mapping of database connections")


class ILoadEvent (IGatewayEvent):
    """Interface for events involved in loading objects."""

    def classify(oid):
        """Returns the classification of the referenced object.
        """


class IStoreEvent (IGatewayEvent):
    """Interface for events involved in storing objects."""

    is_new = Attribute("is_new", """True if the object is new.

    When this attribute is true, gateways should not overwrite
    existing data but instead raise an OIDConflictError if something
    is in the way.  When it is false, gateways should overwrite
    existing data.
    """)


class ISDEvent (IMapperEvent):
    """Base for serialization and deserialization events."""

    obj_db = Attribute("obj_db", "The relevant object database")

    obj = Attribute("obj", "The object being (de)serialized.")

    serializer_name = Attribute("serializer_name", "The serializer in use.")

    upos = Attribute("upos", """The list of unmanaged persistent objects.

    If no attention is paid to unmanaged persistent objects (UPOs),
    they will not notify ZODB when they are changed, and hence can be
    a challenge for the application programmer.  Add UPOs to this list
    so that ZODB will see changes made to them and save the
    corresponding managed persistent object.""")
    
    external = Attribute("external", """The list of external oids.

    The list is built up during (de)serialization.  It contains
    [(oid, subobject)].""")


class IDeserializationEvent(ISDEvent):
    """A helper in the object deserialization process.

    Implementations of ISerializer.deserialize() call
    methods of this interface to restore internal and external
    references.
    """

    def deserialized(name, value):
        """Indicates that a named subobject was deserialized.

        The event records an intra-record reference.  Be careful to
        unwrap non-persistent wrappers around the value before calling
        this method.
        """

    def resolve(name, oid, classification=None):
        """Returns the object identified by an inter-record reference.

        The object should have been stored earlier through a call to
        ISerializationEvent.reference().  The return value is usually
        ghosted initially.

        The event also records an intra-record reference.
        """


class IFullDeserializationEvent(IDeserializationEvent):
    """Deserialization event with features for deserializing remainder data.
    """

    def resolve_internal(ref):
        """Returns the object identified by an intra-record reference.

        'ref' is a tuple containing (serializer_name, name).
        """


class ISerializationEvent(ISDEvent):
    """A helper in the object serialization process.

    Implementations of ISerializer.serialize() call
    methods of this interface to create internal and external
    references.
    """

    def serialized(name, value, is_attribute):
        """Indicates that a named subobject was serialized.

        The event records an intra-record reference.  Be careful to
        unwrap non-persistent wrappers around the value before calling
        this method.
        """

    def referenced(name, value, is_attribute, oid):
        """Notifies the system of an inter-record reference.

        Be careful to unwrap non-persistent wrappers around the value
        before calling this method.  Once the referenced object gets
        stored, the deserialize() method of the serializer will be
        able to find the referenced object by calling
        IDeserializationEvent.resolve().

        The event also records an intra-record reference.
        """

    def ignore(name_or_names):
        """Indicates attribute name(s) to be ignored when serializing.
        """


class IFullSerializationEvent(ISerializationEvent):
    """Serialization event with features for ensuring complete serialization.

    Used for generating a 'remainder pickle'.
    """

    def get_seralized_attributes():
        """Returns the names of all attributes serialized.
        """

    def identify_internal(ob):
        """Returns the intra-record reference for a subobject, if there is one.

        Returns (serializer_name, name) or None.
        """


class ISerializer(Interface):
    """Object serializer / deserializer"""

    schema = Attribute("schema", "The schema used by this component.")

    def can_serialize(obj):
        """Returns true if this serializer can serialize the given object.
        """

    def serialize(event):
        """Returns the state of this part of the object.

        Use the ISerializationEvent to set up internal and external
        references.
        """

    def deserialize(event, state):
        """Fills in the state of this part of the object.

        Use the IDeserializationEvent to resolve external references.
        No return value.
        """


class IFullObjectSerializer(ISerializer):
    """Serializes/deserializes the complete state of objects.

    The serialized state does not need to include the class of the object,
    which is maintained separately.

    IFullObjectSerializers usually delegate to multiple ISerializers
    to do the actual work of (de)serialization.  The schema of
    IFullObjectSerializers is usually a dictionary containing the name
    and schema of its constituent ISerializers.
    """

    def new_instance(event):
        """Returns a new instance.

        event is as IDeserializationEvent.

        If this serializer works with instances of only one class,
        new_instance() should not require the use of a
        classification.  Implementations that need the
        classification argument can return None when classification is
        None, but it may take more work to fetch the classification.

        Implementations should use the IClassFactory implementation
        in the obj_db attribute of the event to load classes.
        """


class IGateway (Interface):
    """Loads and stores data by OID.

    Implementations can store in entire tables, pieces of tables, translate
    for storage in joined tables, or store in some entirely different way.

    Based on _Patterns of Enterprise Application Architecture_
    by Martin Fowler.
    """

    schema = Attribute("schema", "The schema used by this component.")

    def load(event):
        """Loads data.

        event is an ILoadEvent.

        Returns a pair containing the data and a hash of the data.
        The hash value is either an integer or an object that is
        hashable using the Python hash() function.  The hashable
        object is used to detect storage conflicts.

        If no data is available for the requested OID, load() should
        raise a KeyError.
        """

    def store(event, data):
        """Stores data.

        event is an IStoreEvent.

        Returns a new hash value.
        """

    def get_sources(event):
        """Returns source information for an OID.  event is an IGatewayEvent.

        The source information allows the system to poll for changes
        to keep caches in sync with the data.  Where polling is not
        necessary, gateways are free to return None.

        The source information is a dictionary in the format:
        {(source_repository, path): state}.  The repository must be an
        ISourceRepository.  The source and state must be in a form
        recognized by the repository.  Since they are used as
        dictionary keys, both the repositories and paths must be
        hashable.
        """


class IClassifier(Interface):
    """Object classifier

    Implementations of this interface are a little like biologists.
    During serialization, the classify_object() method returns a
    mapping containing the classification of subob (like a biologist
    identifying a creature's genus and species).  During
    deserialization, the classify_state() method decides what kind of
    objects to create for a stored state (like a biologist showing you
    a creature of a certain genus and species).

    The keys in classifications are implementation-dependent.
    """

    gateway = Attribute("gateway", """The classification IGateway.

    Classifiers load and store classifications using a gateway.  This
    attribute allows the system to store the classification of an
    object by calling gateway.store().
    """)

    def classify_object(event):
        """Returns a classification with at least a mapper_name.

        event is an ILoadEvent without a mapper or classification
        (since this method chooses them).
        """

    def classify_state(event):
        """Returns a classification with at least a mapper_name.

        event is an ILoadEvent without a mapper or classification
        (since this method chooses them).

        May load the classification from storage by calling
        self.gateway.load().
        """


class IConfigurableClassifier (IClassifier):
    """Classifier that accepts registrations.
    """

    def add_store_rule(class_name, mapper_name, exact=False,
                        default_extension=None, default_extension_source=None):
        """Adds a rule that says which mapper to use for storing an instance.

        If 'exact' is true, the mapper will not be used for
        subclasses.  'default_extension' provides the default filename
        extension to use when storing to the filesystem.
        'default_extension_source' selects a method of determining the
        extension.  One method is 'content_type', which reads the
        content_type attribute of the object being stored and
        translates the mime type to an extension.  Don't provide both
        'default_extension' and 'default_extension_source'.
        """

    def add_load_rule(criterion, value, mapper_name):
        """Adds a rule that says which mapper to use for loading some data.

        The following values for 'criterion' are common:

        'mapper_name' - matches a previously stored mapper name
                      (useful for mapper name changes)
        'extension' - matches a filename extension
        'generic'  - matches certain kinds of data.  The
                      generic values depend on the classifier, but
                      include 'file', 'directory', 'basepath', and 'root'.
        """


class IOIDGenerator (Interface):
    """A utility for generating OIDs.
    """

    root_oid = Attribute("root_oid", "The OID to use for the root")

    def new_oid(event):
        """Returns a new oid, which should be a string.

        event is an IGatewayEvent.
        """


class IMapper (Interface):
    """A hub for mapping a certain kind of object.
    """
    name = Attribute("name", "The name of this mapper")

    class_name = Attribute(
        "class_name", "The class expected by this mapper (may be empty)")

    serializer = Attribute(
        "serializer", "The IObjectSerializer for this mapper")

    gateway = Attribute("gateway", "The IGateway for this mapper")

    initializers = Attribute("initializers", "A list of IDatabaseInitializers")


class IConfigurableMapper (IMapper):
    """Adds operations to IMapper for configuration.
    """

    def check(my_name):
        """Verifies the mapper configuration is sane.

        Raises a ConfigurationError if inconsistencies are detected.

        'my_name' gives the name of the mapper for debugging purposes.
        """


class IMapperConfiguration (Interface):
    """A configuration of mappers.
    """

    mappers = Attribute("mappers", "Maps mapper name to IMapper")

    classifier = Attribute("classifier", "The IClassifier")

    oid_gen = Attribute("oid_gen", "The IOIDGenerator")

    initializers = Attribute("initializers", "A list of IDatabaseInitializers")

    def check():
        """Verifies the configuration is sane.

        Raises a ConfigurationError if inconsistencies are detected.
        """


class ITPCConnection(Interface):
    """Connection involved in minimal two-phase commit.

    Based on ZODB.Transaction.
    """

    def connect():
        """Opens any resources needed for transactions.  Called only once."""

    def sortKey():
        """Returns a sort key for consistent ordering."""

    def getName():
        """Returns a human-readable name."""

    def begin():
        """Called before the first phase of two-phase commit."""

    def vote():
        """Called upon transition to the second phase of two-phase commit."""

    def abort():
        """Aborts the transaction."""

    def finishWrite():
        """Writes data in the second phase."""

    def finishCommit():
        """Commits in the second phase."""

    def close():
        """Closes resources.  Called only once."""


class ISourceRepository(Interface):
    """Represents a collection of object sources.

    Designed to helps keep a cache in sync with its sources.
    """

    def poll(sources):
        """Returns changed source information.

        The source information is a mapping that maps
        (source_repository, path) to a state object.  The
        source_repository will always be this object (the redundancy
        keeps things simpler for scanners).  This method returns a
        mapping containing only the items of the input dictionary
        whose state has changed.
        """


class IColumnSchema (Interface):
    """A column in a table."""

    name = Attribute(
        "name", "The column name")

    type = Attribute(
        "type", "The type of data held in the column, as a string")

    unique = Attribute(
        "unique", "True if the column is part of the primary key")
