from zope import interface, schema
from zope.configuration import fields
from zope.app.event import interfaces as event_ifaces

class IMetric(interface.Interface):
    """Defines what values are to be collected for an object."""

class IAttributeMetric(IMetric):
    """Retrieves the metric value from an interface field."""

    interface = fields.GlobalInterface(
        title=u'The interface to adapt the object to',
        required=True)

    field_name = fields.PythonIdentifier(
        title=u'The interface field name of the value',
        required=True)

    field_callable = fields.Bool(
        title=u'The interface field name of the value',
        required=False, default=False)

class ISelfMetric(IAttributeMetric):
    """Initializes the object score and uses attribute value."""

class IIndex(interface.Interface):

    initial = interface.Attribute('Initial Score')
    scale = interface.Attribute('Scale')

    def __contains__(obj):
        """Returns True if the object has a score"""

    def changeScoreFor(obj, amount):
        """Change the score for the object by the amount"""

    def getScoreFor(obj):
        """Get the score for an object"""

    def initScoreFor(obj):
        """Initialize the score for the object"""

    def buildScoreFor(obj):
        """Build the score for the object from scratch"""

    def changeScoreFor(obj, amount):
        """Change the score for the object by the amount"""

    def removeScoreFor(obj):
        """Remove the score for the object from the index"""

class IScale(interface.Interface):
    """Translates metric values into scaled values for storage in the
    index.  The scale is also responsible for normalizing raw scores
    into meaningful normalized scores on query time."""

    def fromValue(value):
        """Return the scaled value for the metric value"""

    def toValue(scaled):
        """Return the metric value for the scaled value"""

    def normalize(raw, query=None):
        """Normalize the raw score acording to the scale.  Some scales
        may make use of a query."""

class ISubscription(interface.Interface):
    """Associates a metric with an index and any parameters needed by
    the engine that are specific to the combination of metric and
    index."""

    def getIndex(context=None):
        """Return the index for this subscription.  Some subscriptions
        may accept a context argument for looking up the index."""

class IWeightedSubscription(interface.Interface):
    """A subscription that multiplies metric values by the weight."""

    weight = schema.Float(title=u'Weight', required=False, default=1.0)

class IUtilitySubscription(interface.Interface):
    """The subscribed index is looked up as a utility."""

    utility_interface = fields.GlobalInterface(
        title=u'Index Utility Interface',
        required=False, default=IIndex)

class IUtilityWeightedSubscription(IUtilitySubscription,
                                   IWeightedSubscription):
    """ZCML directive for subscribing a metric to an index with a
    weight."""

class IEngine(interface.Interface):
    """Process a values returned by a metric and update the raw score
    in the index."""

    metric = interface.Attribute('Metric')
    subscription = interface.Attribute('Subscription')
    context = interface.Attribute('Context')

    def initScore():
        """Initialize the score for the context to the index"""
        
    def addValue(value):
        """Add the value to the score for the context in the index"""

    def changeValue(previous, current):
        """Add the difference in values to the score for the context
        in the index"""

    def removeValue(value):
        """Remove the value from the score for the context in the
        index"""

    def removeScore():
        """Remove the score for the context from the index"""

class IChangeScoreEvent(event_ifaces.IObjectEvent):
    """Change an object's score.

    These events are used under normal operation for incrementally
    updating a score in response to normal events on the object.
    These events are dispatched "up" to the scored object."""

class IIndexesScoreEvent(event_ifaces.IObjectEvent):
    """If indexes is not None, the metrics will only apply the score
    changes to the indexes listed."""

    indexes = interface.Attribute('Indexes')

class IBuildScoreEvent(IIndexesScoreEvent):
    """Build an object's score.

    These events are used for maintenance operations to build an
    object's score from scratch.  These events are dispatched
    "down" from the scored object to the objects whose values
    contribute to the score."""

class IAddValueEvent(event_ifaces.IObjectEvent):
    """Add a value from the object's score.

    These events are handled by the metrics to add values to the
    object's score and are independent of the direction of dispatch."""

class IInitScoreEvent(IAddValueEvent):
    """Initialize the object's score only when not building.

    These events are handled by the metrics to initialize the object's
    score and are independent of the direction of dispatch."""

class IRemoveValueEvent(event_ifaces.IObjectEvent):
    """Remove a value from the object's score.

    These events are handled by the metrics to remove values from the
    object's score and are independent of the direction of
    dispatch."""

class ICreated(interface.Interface):
    """List the creators of an object."""

    creators = interface.Attribute('Creators')

class ICreatorLookup(interface.Interface):
    """Lookup creators by id."""
