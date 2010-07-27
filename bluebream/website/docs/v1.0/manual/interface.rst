.. _man-interface:

Interface
=========

Introduction
------------

Interfaces are objects that specify (document) the external behavior
of objects that "provide" them.  An interface specifies behavior
through:

* Informal documentation in a doc string

* Attribute definitions

* Invariants, which are conditions that must hold for objects that
  provide the interface

Some of the motivations for using interfaces are:

* Avoid monolithic design by developing small, exchangeable pieces

* Model external responsibility, functionality, and behavior

* Establish contracts between pieces of functionality

* Document the API

The classic software engineering book Design Patterns by the Gang of
Four recommends that you Program to an interface, not an
implementation.  Defining a formal interface is helpful in
understanding a system.  Moreover, interfaces bring you all the
benefits of Zope Component Architecture.

In some modern programming languages: Java, C#, VB.NET etc,
interfaces are an explicit aspect of the language.  Since Python
lacks interfaces, Zope implements them as a meta-class to inherit
from.

**I can do X**
  Describing the ability to do something is the classical definition
  of an API.  Those abilities are defined and implemented as methods.

**I have X**
  This statement declares the availability of data, which is
  classically associated with schemas.  The data is stored in
  attributes and properties.

**You can do X with me**
  Here we describe the behavior of an object.  Classically there is
  no analog.  However, MIME-types are great example of behavior
  declaration.  This is implemented using empty "marker interfaces"
  as they describe implicit behavior.

The distinction between those three types of contracts was first
pointed out in this form by Philipp von Weitershausen.

Understanding those distinctions is very important, since other
programming languages do not necessarily use all three of these
notions.  In fact, often only the first one is used.

Defining Interfaces
-------------------

* Python has no concept of interfaces
* Not a problem
* Interfaces are just objects
* "Abuse" the class statement to create an interface
* Syntax proposed in PEP 245

In Java, for example, interfaces are special types of objects that
can only serve as interfaces in their intended, limited scope.

An interface from the zope.interface package, on the other hand,
defines the interface by implementing a meta-class, a core concept of
Python.  Thus, interfaces are merely using an existing Python
pattern.

An example
----------

Here is a classic hello world style example::

  >>> class Host(object):
  ...
  ...     def goodmorning(self, name):
  ...         """Say good morning to guests"""
  ...
  ...         return "Good morning, %s!" % name


In the above class, you defined a goodmorning method. If you call the
goodmorning method from an object created using this class, it will
return Good morning, ...!

::

  >>> host = Host()
  >>> host.goodmorning('Jack')
  'Good morning, Jack!'

Here host is the actual object your code uses.  If you want to examine
implementation details you need to access the class Host, either via
the source code or an API documentation tool.

Now we will begin to use the Zope interfaces.  For the class given
above you can specify the interface like this::

  >>> from zope.interface import Interface

  >>> class IHost(Interface):
  ...
  ...     def goodmorning(guest):
  ...         """Say good morning to guest"""

As you can see, the interface inherits from zope.interface.Interface.
This use (abuse?) of Python's class statement is how Zope defines an
interface.  The I prefix for the interface name is a useful
convention.

Declaring interfaces
--------------------

You have already seen how to declare an interface using
zope.interface in previous section.  This section will explain the
concepts in detail.

Consider this example interface::

  >>> from zope.interface import Interface
  >>> from zope.interface import Attribute
 
  >>> class IHost(Interface):
  ...     """A host object"""
  ...
  ...     name = Attribute("""Name of host""")
  ...
  ...     def goodmorning(guest):
  ...         """Say good morning to guest"""

The interface, IHost has two attributes, name and goodmorning.
Recall that, at least in Python, methods are also attributes of
classes.  The name attribute is defined using
zope.interface.Attribute class.  When you add the attribute name to
the IHost interface, you don't set an initial value.  The purpose of
defining the attribute name here is merely to indicate that any
implementation of this interface will feature an attribute named
name.  In this case, you don't even say what type of attribute it has
to be!.  You can pass a documentation string as a first argument to
Attribute.

The other attribute, goodmorning is a method defined using a function
definition.  Note that self is not required in interfaces, because
self is an implementation detail of class.  For example, a module can
implement this interface.  If a module implements this interface,
there will be a name attribute and goodmorning function defined.  And
the goodmorning function will accept one argument.

Now you will see how to connect interface-class-object.  So object is
the real living thing, objects are instances of classes.  And
interface is the actual definition of the object, so classes are just
the implementation details.  This is why you should program to an
interface and not to an implementation.

Now you should familiarize yourself with two more terms to understand
other concepts.  The first one is "provide" and the other one is
"implement".  Object provides interfaces and classes implement
interfaces.  In other words, objects provide interfaces that their
classes implement.  In the above example, host (object) provides
IHost (interface), and Host (class) implements IHost (interface).
One object can provide more than one interface; also one class can
implement more than one interface.  Objects can also provide
interfaces directly, in addition to what their classes implement.

.. note::

    Classes are the implementation details of objects.  In Python,
    classes are callable objects, so why can't other callable objects
    implement an interface? Yes, it is possible.  For any callable
    object you can declare that it produces objects that provide some
    interfaces by saying that the callable object implements the
    interfaces.  The callable objects are generally called
    "factories".  Since functions are callable objects, a function
    can be an implementer of an interface.

Implementing interfaces
-----------------------

To declare a class implements a particular interface, use the
function zope.interface.implements in the class statement.

Consider this example, here Host implements IHost::

  >>> from zope.interface import implements
 
  >>> class Host(object):
  ...
  ...     implements(IHost)
  ...
  ...     name = u''
  ...
  ...     def goodmorning(self, guest):
  ...         """Say good morning to guest"""
  ...
  ...         return "Good morning, %s!" % guest

.. note::

  If you wonder how implements function works, refer the blog post by
  James Henstridge
  (http://blogs.gnome.org/jamesh/2005/09/08/python-class-advisors/)
  . In the adapter section, you will see an adapts function, it is
  also working similarly.

Since Host implements IHost, instances of Host provide IHost.  There
are some utility methods to introspect the declarations.  The
declaration can write outside the class also.  If you don't write
interface.implements(IHost) in the above example, then after defining
the class statement, you can write like this::

  >>> from zope.interface import classImplements
  >>> classImplements(Host, IHost)

Marker interfaces
-----------------

An interface can be used to declare that a particular object belongs
to a special type.  An interface without any attribute or method is
called marker interface.

Here is a marker interface::

  >>> from zope.interface import Interface
 
  >>> class ISpecialGuest(Interface):
  ...     """A special guest"""


This interface can be used to declare an object is a special guest.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
