Introduction
------------

"It was the dawn of the third age of Zope. The Five project was a dream
given form. Its goal: to use Zope 3 technologies in Zope 2.7 by
creating a Zope 2 product where Zope 3 and Zope 2 could work out their
differences peacefully." -- Babylon 5, creatively quoted

"The Law of Fives states simply that: ALL THINGS HAPPEN IN FIVES, OR
ARE DIVISIBLE BY OR ARE MULTIPLES OF FIVE, OR ARE SOMEHOW DIRECTLY OR
INDIRECTLY RELATED TO FIVE.

THE LAW OF FIVES IS NEVER WRONG." -- Principia Discordia

How to install Five
-------------------

See ``INSTALL.txt``.

How to use Five
---------------

Five is only useful on the Python (Product) level, not from within the
Zope Management Interface. 

Adapters
--------

The immediate thing that Five brings to do the table are
adapters. This section goes through some demo code to explain how
everything is tied together. ``demo/FiveDemo`` is a demo Product you
can install and examine that has all the presented here together.

Zope 3 adapters depend on Zope 3 interfaces. To create a Zope 3
interface you need to subclass it from
``zope.interface.Interface``. Here is an example::

  from zope.interface import Interface

  class IMyInterface(Interface):
      """This is a Zope 3 interface.
      """
      def someMethod():
          """This method does amazing stuff.
          """

Now to make some class declare that it implements this interface, you
need to use the ``implements()`` function in the class::

  from zope.interface import implements
  from interfaces import IMyInterface

  class MyClass:
      implements(IMyInterface)

      def someMethod(self):
           return "I am alive! Alive!"

For an explanation of the relation of Zope 3 interfaces to Zope 2
interfaces, see below.

Now let's set up the interface that we are adapting to::

  class INewInterface(Interface):
      """The interface we adapt to.
      """

      def anotherMethod():
          """This method does more stuff.
          """

Next we'll work on the class that implements the adapter. The
requirement to make a class that is an adapter is very simple; you
only need to take a context object as the constructor. The context
object is the object being adapted. An example::

  from zope.interface import implements
  from interfaces import INewInterface

  class MyAdapter:
      implements(INewInterface)
 
      def __init__(self, context):
          self.context = context

      def anotherMethod(self):
          return "We have adapted: %s" % self.context.someMethod()

Next, we hook it all up using zcml. If the classes are in a module
called ``classes.py`` and the interfaces in a module called
``interfaces.py``, we can declare ``MyAdapter`` to be an adapter for
``IMyInterface`` to ``INewInterface`` like this (in a file called
``configure.zcml``)::

  <configure xmlns="http://namespaces.zope.org/zope">

    <adapter 
      for=".interfaces.IMyInterface"
      provides=".interfaces.INewInterface"
      factory=".classes.MyAdapter" /> 
    
  </configure>

The next step is to read ``configure.zcml`` so Zope can find these
declarations. Do this by placing the following in the ``__init__.py``
of your Zope product::

  from Products.Five import zcml
  import Products
   
  def initialize(context):
      zcml.process('configure.zcml', package=Products.FiveDemo)        
 
Any class that implements ``INewInterface`` can now be adapted to
``INewInterface``, like this::

  from zope.component import getAdapter
  from classes import MyClass
  from interfaces import INewInterface

  object = MyClass()
  adapted = getAdapter(object, INewInterface)
  print adapted.anotherMethod()

A shortcut for ``getAdapter()`` is to call the interface directly,
like this::

  adapted = INewInterface(object)

Views in Five
-------------

This section will give a brief introduction on how to use the five
view system. ``demo/FiveViewsDemo`` is a demo Product you can install
and examine that has all the presented here tied together, please
consult it for more details. ``tests/products/FiveTest`` actually
contains a more detailed set of test views, trying a number of
features. Finally, read up on the way Zope 3 does it. While Five is a
subset of Zope 3 functionality and has been adapted to work with Zope
2, much of Zope 3's documentation still works.

Five enables you to create views for your own objects, or even built-in
Zope objects, as long as two things are the case:

* The object provides an Zope 3 interface, typically through its class.

* The object (typically its class) is made viewable.

Typically you give your classes an interface using the ``implements``
directive in the class body::

  class MyClass:
      implements(ISomeInterface)

For existing objects that you cannot modify this is not
possible. Instead, we provide a ZCML directive to accomplish this. As
an example, to make Zope's ``Folder`` (and all its subclasses)
implement ``IFolder`` (an interface you defined), you can do the
following in ZCML::

  <five:implements class="OFS.Folder.Folder" 
                   interface=".interfaces.IFolder" />

``five`` in this case refers to the XML namespace for Five,
``http://namespace.zope.org/five``.

To make an object viewable through Five your object needs to mix in
``Viewable``, which can be imported from Products.Five.api. For
instance::

  from Products.Five.api import Viewable

  class MyClass(OFS.SimpleItem.Item, Viewable):
      implements(ISomeInterface)

For existing Zope objects, this is not easily possible. We've provided
another ZCML directive however to take care of that. To continue our
example, to make Zope's ``Folder`` viewable through Five, you need to
declare this in ZCML as well:

  <five:viewable class="OFS.Folder.Folder"/>

This makes Folder look up Zope 3 views first, and then if they cannot be
found, fall back on the regular Zope 2 views. This allows the ZMI to work
still, but new views can be added on the fly.

Note that at the point of writing it is only possible to make an object
viewable through ZCML if this object does not already provide its own
``__bobo_traverse__`` method.

Views in Five are simple classes. The only requirements for a Five
view class are:

  * They need an ``__init__()`` that take a context and a request
    attribute. Typically this comes from a base class, such as
    ``FiveView``.

  * They need to be initialized with the Zope 2 security system, as
    otherwise you cannot use the view. 

  * This also means they need to be part of the Zope 2 acquisition
    system, as this is a requirement for Zope 2 security to
    function. The ``BrowserView`` base class, available from
    ``Products.Five.api``, already inherits from
    ``Acquisition.Explicit`` to make this be the case. Acquisition is
    explicit so no attributes can be acquired by accident.

An example of a simple view::
 
  from Products.Five.api import BrowserView

  class SimpleFolderView(BrowserView):
      security = ClassSecurityInfo()

      security.declarePublic('eagle')
      def eagle(self):
          """Test
          """
          return "The eagle has landed: %s" % self.context.objectIds()

  InitializeClass(SimpleFolderView)

Note that it is not a good idea to give a view class its own
``index_html``, as this confuses Five's view lookup machinery.

As you can see, the class is initialized with the Zope 2 security
system. This view uses methods in Python, but you can also use other
Zope 2 mechanisms such as ``PageTemplateFile``.

Finally, we need to hook up the pages through ZCML::

  <browser:page 
    for=".interfaces.IFolder"
    class=".browser.SimpleFolderView"
    attribute="eagle"
    name="eagle.txt"
    permission="zope.ViewManagementScreens"
    />

``browser`` in this refers to the XML namespace of Zope 3 for browser
related things; it's
``http://namespace.zope.org/browser``. ``permission`` declares the
Zope 2 permission needs in order to access this view. The file
``permissions.zcml`` in Five contains a mapping of Zope 2 permissions
to their Zope 3 names.

Interfaces in Zope 2 versus Zope 3
----------------------------------

Zope 2 has used the ``__implements__`` class attribute for interface
declarations.  Zope 2 cannot detect Zope 3 interfaces and the
Zope 3 machinery cannot detect Zope 2 interfaces. This is a good
thing, as Zope 2 has no way to deal with Zope 3 interfaces, and Zope 3
cannot comprehend Zope 2 interfaces. It also means you can safely
these interface declarations in a class. It's a rare case where you
need this though; you're better off just switching to ``implements()``
for your application if you are using Five. 

Switching from Zope 2 interfaces to Zope 3 interfaces is easy -- just
make your interfaces inherit from ``zope.interface.Interface`` instead
of ``Interface.Interface`` (or ``Interface.Base``). This should get
you going and your application may very well still work. Later on, you
will also have to change calls to ``isImplementedBy`` and such in your
application to ``providedBy``, as ``isImplementedBy`` has been
deprecated (you'll see the DeprecationWarnings in your log).
