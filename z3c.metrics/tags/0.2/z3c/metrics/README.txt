.. -*-Doctest-*-

===========
z3c.metrics
===========

Create two document indexes.

    >>> from z3c.metrics import testing
    >>> foo_doc_index = testing.Index()
    >>> bar_doc_index = testing.Index()

Create one creator index.

    >>> creator_index = testing.Index()

Set the scales for the indexes.  The defaults for scales is a half
life of one unit.  In the case of a datetime scale, the half life is
one year.

    >>> from z3c.metrics import scale
    >>> one_year_scale = scale.ExponentialDatetimeScale()
    >>> foo_doc_index.scale = one_year_scale
    >>> creator_index.scale = one_year_scale

Specify a half life of two years for the second document index.

    >>> two_year_scale = scale.ExponentialDatetimeScale(
    ...     scale_unit=scale.one_year*2)
    >>> bar_doc_index.scale = two_year_scale

Create a self metric that scores the creation dates of the object
itself.

    >>> from z3c.metrics import interfaces, metric
    >>> self_metric = metric.SelfMetric(
    ...     field_name="created", interface=interfaces.ICreated)

Register the self metric event handlers so that they are run on
documents themselves for their own scores.

    >>> from zope import component
    >>> component.provideHandler(
    ...     factory=self_metric.initSelfScore,
    ...     adapts=[testing.IDocument, interfaces.IAddValueEvent])
    >>> component.provideHandler(
    ...     factory=self_metric.removeSelfScore,
    ...     adapts=[testing.IDocument, interfaces.IRemoveValueEvent])

Create an other metric that scores creation dates of descendants.

    >>> desc_metric = metric.OtherMetric(
    ...     interface=interfaces.ICreated,
    ...     field_name="created", field_callable=True)

Register the other metric event handlers so that they are run on
descendants of documents for document scores.

    >>> component.provideHandler(
    ...     factory=desc_metric.addOtherValue,
    ...     adapts=[testing.IDescendant,
    ...             interfaces.IAddValueEvent,
    ...             testing.IDocument])
    >>> component.provideHandler(
    ...     factory=desc_metric.removeOtherValue,
    ...     adapts=[testing.IDescendant,
    ...             interfaces.IRemoveValueEvent,
    ...             testing.IDocument])

Creat an init metric that initializes the score for new creators.

    >>> from zope.app.security import interfaces as security_ifaces
    >>> init_metric = metric.InitMetric()

Register the init metric event handlers so that they are run when
creators are added and removed.

    >>> component.provideHandler(
    ...     factory=init_metric.initSelfScore,
    ...     adapts=[security_ifaces.IPrincipal,
    ...             interfaces.IInitScoreEvent])
    >>> component.provideHandler(
    ...     factory=init_metric.removeSelfScore,
    ...     adapts=[security_ifaces.IPrincipal,
    ...             interfaces.IRemoveValueEvent])

Register the other metric event handlers so that they are run on
documents for creators' scores.

    >>> other_metric = metric.OtherMetric(
    ...     field_name="created", interface=interfaces.ICreated)

    >>> from zope.app.security import interfaces as security_ifaces
    >>> component.provideHandler(
    ...     factory=other_metric.addOtherValue,
    ...     adapts=[testing.IDocument,
    ...             interfaces.IAddValueEvent,
    ...             security_ifaces.IPrincipal])
    >>> component.provideHandler(
    ...     factory=other_metric.removeOtherValue,
    ...     adapts=[testing.IDocument,
    ...             interfaces.IRemoveValueEvent,
    ...             security_ifaces.IPrincipal])

Register the other metric event handlers so that they are run on
descendants of documents for creators' scores.

    >>> component.provideHandler(
    ...     factory=desc_metric.addOtherValue,
    ...     adapts=[testing.IDescendant,
    ...             interfaces.IAddValueEvent,
    ...             security_ifaces.IPrincipal])
    >>> component.provideHandler(
    ...     factory=desc_metric.removeOtherValue,
    ...     adapts=[testing.IDescendant,
    ...             interfaces.IRemoveValueEvent,
    ...             security_ifaces.IPrincipal])

Create a principal as a creator.

    >>> from z3c.metrics import testing
    >>> authentication = component.getUtility(
    ...     security_ifaces.IAuthentication)
    >>> baz_creator = testing.Principal()
    >>> authentication['baz_creator'] = baz_creator

Create a root container.

    >>> root = testing.setUpRoot()

Create one document before any metrics are added to any indexes.

    >>> foo_doc = testing.Document()
    >>> foo_doc.created = scale.epoch
    >>> foo_doc.creators = ('baz_creator',)
    >>> root['foo_doc'] = foo_doc

Create a descendant of the document that will be included in the score
for the document.

    >>> now = scale.epoch+scale.one_year*2
    >>> foo_desc = testing.Descendant()
    >>> foo_desc.created = now
    >>> foo_desc.creators = ('baz_creator',)
    >>> foo_doc['foo_desc'] = foo_desc

The indexes have no metrics yet, so they have no scores for the
documents.

    >>> foo_doc_index.getScoreFor(foo_doc)
    Traceback (most recent call last):
    KeyError: ...
    >>> bar_doc_index.getScoreFor(foo_doc)
    Traceback (most recent call last):
    KeyError: ...
    >>> creator_index.getScoreFor(baz_creator)
    Traceback (most recent call last):
    KeyError: ...

Add the self metric to the first document index with the default
weight.

    >>> from z3c.metrics import subscription
    >>> foo_self_sub = subscription.LocalWeightedSubscription(
    ...     foo_doc_index)
    >>> component.provideSubscriptionAdapter(
    ...     factory=foo_self_sub.getChangeScoreEngine,
    ...     adapts=[interfaces.IMetric, testing.IDocument,
    ...             interfaces.IChangeScoreEvent])
    >>> component.provideSubscriptionAdapter(
    ...     factory=foo_self_sub.getBuildScoreEngine,
    ...     adapts=[interfaces.IMetric, testing.IDocument,
    ...             interfaces.IBuildScoreEvent])

Add the self metric to the other document index but with a weight of
two.

    >>> bar_self_sub = subscription.LocalWeightedSubscription(
    ...     bar_doc_index)
    >>> bar_self_sub.weight = 2.0
    >>> component.provideSubscriptionAdapter(
    ...     factory=bar_self_sub.getChangeScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             testing.IDocument,
    ...             interfaces.IChangeScoreEvent])
    >>> component.provideSubscriptionAdapter(
    ...     factory=bar_self_sub.getBuildScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             testing.IDocument,
    ...             interfaces.IBuildScoreEvent])

Also add the other metric to this index for descendants of documents.

    >>> bar_desc_sub = subscription.LocalWeightedSubscription(
    ...     bar_doc_index)
    >>> component.provideSubscriptionAdapter(
    ...     factory=bar_desc_sub.getChangeScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             testing.IDocument,
    ...             interfaces.IChangeScoreEvent,
    ...             testing.IDescendant])
    >>> component.provideSubscriptionAdapter(
    ...     factory=bar_desc_sub.getBuildScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             testing.IDocument,
    ...             interfaces.IBuildScoreEvent,
    ...             testing.IDescendant])

Add the init metric to the creator index for creators.

    >>> creator_init_sub = subscription.LocalWeightedSubscription(
    ...     creator_index)
    >>> component.provideSubscriptionAdapter(
    ...     factory=creator_init_sub.getChangeScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             security_ifaces.IPrincipal,
    ...             interfaces.IChangeScoreEvent])
    >>> component.provideSubscriptionAdapter(
    ...     factory=creator_init_sub.getBuildScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             security_ifaces.IPrincipal,
    ...             interfaces.IBuildScoreEvent])

Add the other metric to the creator index for document creators with a
weight of two.

    >>> creator_doc_sub = subscription.LocalWeightedSubscription(
    ...     creator_index)
    >>> creator_doc_sub.weight = 2.0
    >>> component.provideSubscriptionAdapter(
    ...     factory=creator_doc_sub.getChangeScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             security_ifaces.IPrincipal,
    ...             interfaces.IChangeScoreEvent,
    ...             testing.IDocument])
    >>> component.provideSubscriptionAdapter(
    ...     factory=creator_doc_sub.getBuildScoreEngine,
    ...     adapts=[interfaces.IMetric, security_ifaces.IPrincipal,
    ...             interfaces.IBuildScoreEvent, testing.IDocument])

Add the other metric to the creator index for document descendant
creators with the default weight.

    >>> creator_desc_sub = subscription.LocalWeightedSubscription(
    ...     creator_index)
    >>> component.provideSubscriptionAdapter(
    ...     factory=creator_desc_sub.getChangeScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             security_ifaces.IPrincipal,
    ...             interfaces.IChangeScoreEvent,
    ...             testing.IDescendant])
    >>> component.provideSubscriptionAdapter(
    ...     factory=creator_desc_sub.getBuildScoreEngine,
    ...     adapts=[interfaces.IMetric,
    ...             security_ifaces.IPrincipal,
    ...             interfaces.IBuildScoreEvent,
    ...             testing.IDescendant])

Build scores for the document.

    >>> foo_doc_index.buildScoreFor(foo_doc)
    >>> bar_doc_index.buildScoreFor(foo_doc)

Now the document has different scores in both indexes.

    >>> foo_doc_index.getScoreFor(foo_doc, query=now)
    0.25
    >>> bar_doc_index.getScoreFor(foo_doc, query=now)
    2.0

Build the score for the creator.

    >>> creator_index.buildScoreFor(baz_creator)

Now the creators have scores in the creator index.

    >>> creator_index.getScoreFor(baz_creator, query=now)
    1.5

Add a new creator.

    >>> qux_creator = testing.Principal()
    >>> authentication['qux_creator'] = qux_creator

The new creator now also has the correct score

    >>> creator_index.getScoreFor(qux_creator, query=now)
    0.0

Create a new document with two creators.

    >>> bar_doc = testing.Document()
    >>> bar_doc.created = now
    >>> bar_doc.creators = ('baz_creator', 'qux_creator')
    >>> root['bar_doc'] = bar_doc

The indexes have scores for the new document.

    >>> foo_doc_index.getScoreFor(bar_doc, query=now)
    1.0
    >>> bar_doc_index.getScoreFor(bar_doc, query=now)
    2.0
    >>> creator_index.getScoreFor(baz_creator, query=now)
    3.5
    >>> creator_index.getScoreFor(qux_creator, query=now)
    2.0

The scores are the same if rebuilt.

    >>> foo_doc_index.buildScoreFor(bar_doc)
    >>> bar_doc_index.buildScoreFor(bar_doc)
    >>> creator_index.buildScoreFor(baz_creator)
    >>> creator_index.buildScoreFor(qux_creator)

    >>> foo_doc_index.getScoreFor(bar_doc, query=now)
    1.0
    >>> bar_doc_index.getScoreFor(bar_doc, query=now)
    2.0
    >>> creator_index.getScoreFor(baz_creator, query=now)
    3.5
    >>> creator_index.getScoreFor(qux_creator, query=now)
    2.0

Later, add two descendants for this document.

    >>> now = scale.epoch+scale.one_year*4
    >>> bar_desc = testing.Descendant()
    >>> bar_desc.created = now
    >>> bar_doc['bar_desc'] = bar_desc
    >>> baz_desc = testing.Descendant()
    >>> baz_desc.created = now
    >>> bar_doc['baz_desc'] = baz_desc

The scores reflect the addtions.

    >>> foo_doc_index.getScoreFor(bar_doc, query=now)
    0.25
    >>> bar_doc_index.getScoreFor(bar_doc, query=now)
    3.0

The scores for the other document also reflect the advance of time.

    >>> foo_doc_index.getScoreFor(foo_doc, query=now)
    0.0625
    >>> bar_doc_index.getScoreFor(foo_doc, query=now)
    1.0
    >>> creator_index.getScoreFor(baz_creator, query=now)
    0.875
    >>> creator_index.getScoreFor(qux_creator, query=now)
    0.5

The scores are the same if rebuilt.

    >>> foo_doc_index.buildScoreFor(foo_doc)
    >>> bar_doc_index.buildScoreFor(foo_doc)
    >>> foo_doc_index.buildScoreFor(bar_doc)
    >>> bar_doc_index.buildScoreFor(bar_doc)
    >>> creator_index.buildScoreFor(baz_creator)
    >>> creator_index.buildScoreFor(qux_creator)

    >>> foo_doc_index.getScoreFor(foo_doc, query=now)
    0.0625
    >>> bar_doc_index.getScoreFor(foo_doc, query=now)
    1.0
    >>> foo_doc_index.getScoreFor(bar_doc, query=now)
    0.25
    >>> bar_doc_index.getScoreFor(bar_doc, query=now)
    3.0
    >>> creator_index.getScoreFor(baz_creator, query=now)
    0.875
    >>> creator_index.getScoreFor(qux_creator, query=now)
    0.5

Remove one of the descendants.

    >>> del bar_doc['bar_desc']

The scores reflect the deletion of the descendant.

    >>> foo_doc_index.getScoreFor(bar_doc, query=now)
    0.25
    >>> bar_doc_index.getScoreFor(bar_doc, query=now)
    2.0

The scores are the same if rebuilt.

    >>> foo_doc_index.buildScoreFor(bar_doc)
    >>> bar_doc_index.buildScoreFor(bar_doc)

    >>> foo_doc_index.getScoreFor(bar_doc, query=now)
    0.25
    >>> bar_doc_index.getScoreFor(bar_doc, query=now)
    2.0

Remove one of the documents.

    >>> del root['bar_doc']

The document indexes no longer have scores for the document.

    >>> foo_doc_index.getScoreFor(bar_doc)
    Traceback (most recent call last):
    KeyError: ...
    >>> bar_doc_index.getScoreFor(bar_doc)
    Traceback (most recent call last):
    KeyError: ...

The creator indexes reflect the change.

    >>> creator_index.getScoreFor(baz_creator, query=now)
    0.375
    >>> creator_index.getScoreFor(qux_creator, query=now)
    0.0

XXX
===

For example, a metric may collect the date the object itself was
created.  While another metric might collect the dates certain kinds
of descendants were created.  Another yet might collect rating values
from certain kinds of descendants.

An index uses one or more metrics to provide efficient lookup of
normailized values for objects.  One common use for such values is
sorting a set of objects.  The score an index stores for an object is
the sum of the scores determined for each metric.

XXX Metrics
===========

Metrics define the values that constitute the score for an object in a
given metric index.  Metrics update an object's score incrementally
and as such can only use values whose both previous and new values can
be retrieved on change.

For example, one value may be the creation date of a descendant.  When
such a value changes, the metric can assume there was no previous
value.  Likewise, when such an object is deleted, the metric must be
able to retrieve the creation date from the object before it is
deleted in order to make the incremental adjustment.

This is mostly a concern if a metric's values are mutable, then the
metric must be informed whenever that value changes in such a way that
it has access to both the preveious and new values.  This should most
commonly be done using events to which the metric subscribes handlers.

A metric is a component that knows how to look up metric values for a
given object.

Note that if we don't count on event order, then building an object
score from scratch requires explicitly initializing the index and
ensuring that none of the event handlers will initialize the socre for
the build score event.  Otherwise, it's possible that the initializing
event handler will be called after other add value events and negate
their effect.
