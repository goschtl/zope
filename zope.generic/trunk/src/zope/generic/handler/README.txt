===============
Generic Handler
===============

The directive generic:handler allows to register operation-based object event
handlers.


Hander convenience subscriber
-----------------------------

First we declare a key interface:

    >>> class IFoo(interface.Interface):
    ...    """The key interface."""

    ... <generic:interface
    ...     interface="example.IFoo"
    ...     type="zope.generic.face.IKeyfaceType"
    ...     />
    ... ''')

During the notification process we invoke the declared operations. In our example
we are defining a simple handler, but you could use object providing IOperation
or interfaces providing IOperationType too:

    >>> def simplehandler(context, event):
    ...    print 'Guguseli!'


That we can register the generic:handler directive we have also to choose a
certain event-interface or -class:

    >>> registerDirective('''
    ... <generic:handler
    ...     keyface="example.IFoo"
    ...     event="zope.component.interfaces.IObjectEvent"
    ...     operations="example.simplehandler"
    ...     />
    ... ''') 

Now we can check out the registered handler:

    >>> class Foo(object):
    ...     interface.implements(IFoo)

    >>> foo = Foo()

    >>> from zope.component.interfaces import IObjectEvent
    >>> from zope.component.interfaces import ObjectEvent
    >>> from zope.event import notify

    >>> event = ObjectEvent(foo)
    >>> notify(event)
    Guguseli!
    
    >>> notify(ObjectEvent(object()))
