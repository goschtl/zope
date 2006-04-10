=================
Directly Provides
=================

The `zope.interface` package offers the powerful mechanism of directly provided
interfaces that means instance-specific interfaces.

Directly provided interfaces today have the most important impact to 
interface-based lookups for example within the adapter registry, therefore the 
directly provided interface can fully control/determine the behavior of
applications based on the component architecture.

The problem is that those interface cannot be controlled properly:

- Ordering depends on the chronological order, but often this order
  cannot asserted properly other a later interface is hidden by an
  earlier one.

- No event notification even though the whole adaption based behavior might
  have changed.

- Sometimes an other order that the cronological should be asserted. That
  means dedicated directly provided interfaces should be prepended someway.

Those lacks might lead to mistaken lookups. The scope of this package
is to provide better controll over the directly provided mechanism.

Now we will explore this behavior in a small showcase. There are four
interfaces IA, IB, IC, ID marking instances that will be adapted. The interface
IResult is the target resp. provided interface. The class A and the adapters 
ResultForA, ResultForB, ResultForC, ResultForD are representing corresponding 
sample implementations:

    >>> class IA(interface.Interface):
    ...     pass

    >>> class IB(interface.Interface):
    ...     pass

    >>> class IC(interface.Interface):
    ...     pass

    >>> class ID(interface.Interface):
    ...     pass

    >>> class IResult(interface.Interface):
    ...     pass

    >>> class A(object):
    ...     interface.implements(IA)

    >>> class ResultForA(object):
    ...     interface.implements(IResult)
    ...     component.adapts(IA)
    ...     def __init__(self, context):
    ...         pass

    >>> class ResultForB(object):
    ...     interface.implements(IResult)
    ...     component.adapts(IB)
    ...     def __init__(self, context):
    ...         pass

    >>> class ResultForC(object):
    ...     interface.implements(IResult)
    ...     component.adapts(IC)
    ...     def __init__(self, context):
    ...         pass

    >>> class ResultForD(object):
    ...     interface.implements(IResult)
    ...     component.adapts(ID)
    ...     def __init__(self, context):
    ...         pass

    >>> component.provideAdapter(ResultForA)
    >>> component.provideAdapter(ResultForB)
    >>> component.provideAdapter(ResultForC)
    >>> component.provideAdapter(ResultForD)

First we adapt an instance of `A` regularly:

    >>> a = A()
    >>> IResult(a)
    <example.ResultForA object at ...>

If we directly provides an interface, for example IB, the
corresponding adapter `ResultForB` will be looked up:

    >>> interface.directlyProvides(a, IB)
    >>> IResult(a)
    <example.ResultForB object at ...>

    >>> interface.alsoProvides(a, IC)
    >>> IResult(a)
    <example.ResultForB object at ...>

Given the fact that different orthagonal application such as the site
framework uses the directly provided mechanism it is not possible
to determine the order of directly provided interfaces in respect to
the point in time when it will be setted:

    >>> a = A()

    >>> interface.directlyProvides(a, IC) 
    >>> IResult(a)
    <example.ResultForC object at ...>

    >>> interface.alsoProvides(a, IB)
    >>> IResult(a)
    <example.ResultForC object at ...>

As long as different directly provided interfaces do not overlap
features this unordered aspect is not relevant.

One possibility is to rely heavly on this directly provides mechanism
to model business domains using generic base classes and marker interfaces
differing the business types. All features of generic business objects
could be provided by adaption. In those edge cases it would be more
comfortable to have partial control over the directly provided mechanism.

The package `zope.generic.directlyprovides` offers the functionality to
control directly provided interfaces partially. In the next showcase
we implement a generic class Prependes. The attribute `prepended` offers
a list of interfaces that should be prepended to the directly provided
interfaces.

First we define an interface deriving from IProvides:

    >>> from zope.interface.interfaces import IInterface
    >>> from zope.generic.directlyprovides import api

    >>> class IPrepender(api.IProvides):
    ...
    ...     first = schema.Tuple(title=u'First',
    ...         description=u'Prepend the listed interfaces first.',
    ...         default=(),
    ...         value_type=schema.Object(schema=IInterface))
    ...
    ...     second = schema.Tuple(title=u'Second',
    ...         description=u'Prepend the listed interfaces second.',
    ...         default=(),
    ...         value_type=schema.Object(schema=IInterface))

Then we have to implement the interface within the class Prepender.

The *provides* defines the relevant attributes that contains the
interfaces that should be prepented to the directly provided interfaces.

We can use the decorator `updateProvides` or the property UpdateProvides
to update the directly provide mechanism if the value of the prepended 
attribute is newly set.

We declare the field that stores the value and we can determine optional
pre- and post-hooks that should offer three parameters `self`, `new` 
and `old` as signature:

    >>> def before_hook(self, new, old):
    ...     print 'before'

    >>> def after_hook(self, new, old):
    ...     print 'after',
    ...     print str(tuple([iface.__name__ for iface in old])),
    ...     print 'to ' + str(tuple([iface.__name__ for iface in new]))

If the directly provided interfaces has changed an directly provides event
is notified. We register an handler for this event:

    >>> from zope.interface import directlyProvidedBy
    >>> def notifyDirectlyProvidesModifiedEvent(component, event):
    ...     print 'directlyProvided changed', str(tuple([iface.__name__  
    ...         for iface in interface.directlyProvidedBy(event.object)]))

    >>> component.provideHandler(notifyDirectlyProvidesModifiedEvent,
    ...     (api.IProvides, api.IDirectlyProvidesModifiedEvent))

    >>> from zope.app.event.interfaces import IObjectModifiedEvent

    >>> def notifyObjectModifiedEvent(first, second=None):
    ...     if second:
    ...         print 'Object modified (multi subscriber), ',
    ...         first = second
    ...     else:
    ...         print 'Object modified (single subscriber), ',
    ...     description = first.descriptions[0]
    ...     print description.interface.__name__, description.attributes

    >>> component.provideHandler(notifyObjectModifiedEvent,
    ...     (IObjectModifiedEvent,))

    >>> component.provideHandler(notifyObjectModifiedEvent,
    ...     (IPrepender, IObjectModifiedEvent))

Now we are implementing an example class using the before- and after-hook.
For documentation purposes we use for the `first` attribute the decorator and
for the `second` attribute the property:

    >>> class Prepender(object):
    ...
    ...     interface.implements(IPrepender)
    ...     api.provides('first', 'second')
    ...
    ...     def _g_first(self):
    ...         return self.__dict__.get('prepended', ())
    ...
    ...     @api.updateProvides(IPrepender['first'], before_hook, after_hook)
    ...     def _s_first(self, value):
    ...         if value:
    ...             self.__dict__['prepended'] = value
    ...         else:
    ...             del self.__dict__['prepended']
    ...
    ...     first = property(_g_first, _s_first)
    ...
    ...     second = api.UpdateProvides(IPrepender['second'], before_hook, after_hook)

Now, we are going to use our example implementation. At the beginning
the generic prepended instance does not provide any adaptable interface,
therefore an error is raised if we try to adapt to IResult:

    >>> p = Prepender()
    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    []
    >>> IResult(p)
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt'...)

After that we provide IB directly:

    >>> interface.directlyProvides(p, IB) 
    directlyProvided changed ('IB',)

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['IB']
    >>> IResult(p)
    <example.ResultForB object at ...>

Another assignment is appended:

    >>> interface.alsoProvides(p, IA)
    directlyProvided changed ('IB', 'IA')

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['IB', 'IA']

    >>> IResult(p)
    <example.ResultForB object at ...>

But if we use our prepend mechanism the interface is prepended:

    >>> p.second = (ID, )
    before
    directlyProvided changed ('ID', 'IB', 'IA')
    after () to ('ID',)

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['ID', 'IB', 'IA']

    >>> IResult(p)
    <example.ResultForD object at ...>

    >>> p.first = (IC, )
    before
    directlyProvided changed ('IC', 'ID', 'IB', 'IA')
    after () to ('IC',)

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['IC', 'ID', 'IB', 'IA']

    >>> IResult(p)
    <example.ResultForC object at ...>

The value of the decorated attribute or the property will be only set if the
old and new value differs:

    >>> p.first = (IC, )
    >>> p.second = (ID, )

We can remove the prepended interface setting an empty tuple:

    >>> p.first = ()
    before
    directlyProvided changed ('ID', 'IB', 'IA')
    after ('IC',) to ()

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['ID', 'IB', 'IA']

    >>> IResult(p)
    <example.ResultForD object at ...>

If the twice the same interface is set only the first is accepted. 
Attention, in this case no directly provides event is notified, because
the order of the directly provided interfaces did not change:

    >>> p.first = (ID,)
    before
    after () to ('ID',)
    
    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['ID', 'IB', 'IA']

We can add more than one or switch them:

    >>> p.first = (ID, IC)
    before
    directlyProvided changed ('ID', 'IC', 'IB', 'IA')
    after ('ID',) to ('ID', 'IC')

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['ID', 'IC', 'IB', 'IA']
    >>> IResult(p)
    <example.ResultForD object at ...>

    >>> p.first = (IC, ID)
    before
    directlyProvided changed ('IC', 'ID', 'IB', 'IA')
    after ('ID', 'IC') to ('IC', 'ID')

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['IC', 'ID', 'IB', 'IA']
    >>> IResult(p)
    <example.ResultForC object at ...>

We can remove a regular directly provided:

    >>> interface.directlyProvides(p, interface.directlyProvidedBy(p) - IB)
    directlyProvided changed ('IC', 'ID', 'IA')

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['IC', 'ID', 'IA']
    >>> IResult(p)
    <example.ResultForC object at ...>

But we cannot remove a prepended one. Attention, in this case no directly provides
event is notified, because the directly provided interfaces
did not change:

    >>> interface.directlyProvides(p, interface.directlyProvidedBy(p) - IC)

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['IC', 'ID', 'IA']
    >>> IResult(p)
    <example.ResultForC object at ...>

If we like to remove prepended one, we have to set the corresponding attribute.
Take care, sometimes a second prepended still offfers an removed interface:

    >>> p.first = (IA,)
    before
    directlyProvided changed ('IA', 'ID')
    after ('IC', 'ID') to ('IA',)

    >>> [iface.__name__ for iface in interface.directlyProvidedBy(p)]
    ['IA', 'ID']
    >>> IResult(p)
    <example.ResultForA object at ...>

There is event dispatcher to object modified events provided if the object
providing IProvides is marked by IObjectModifiedEventDispatchingProvides:

    >>> interface.classImplements(Prepender, 
    ...     api.IObjectModifiedEventDispatchingProvides)

    >>> p.first = (IB,)
    before
    directlyProvided changed ('IB', 'ID')
    Object modified (multi subscriber),  IProvides ('__provides__',)
    Object modified (single subscriber),  IProvides ('__provides__',)
    after ('IA',) to ('IB',)
