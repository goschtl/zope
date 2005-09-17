========
Pagelets
========

This package provides a framework to develop componentized Web GUI
applications. Instead of describing the content of a page using a single
template or static system of templates and METAL macros, regions (called
slots) can be defined and are filled dynamically with content based on the
setup of the application.

The Design
----------

UML Diagram
~~~~~~~~~~~
                      _________
                     |         |
                     | Context |
                     |_________|
                          ^
                          |
                          |*
                      ____|____
                     |         |
                     |   View  |
                     |_________|
                          |
                          |
                          |* a view is composed of slots
                      ____v____
                     |          |
                     | ViewSlot |
                     |__________|
                          |
                          |
                          |* a slot contains a list of viewlets
                      ____v____        _____________
                     |         |      |             |
                     | Viewlet |------| ViewletType |
                     |_________|*     |_____________|
                          ^
                         /_\
              ____________|____________
             |                         |
         ____|____                 ____|____
        |         |               |         |
        | Pagelet |               | Portlet |
        |_________|               |_________|

Natively, Zope 3 allows us to associate one or more views to a given
object. Those views are either registered for the provided interfaces of the
object or the object itself. In a view, usually a template, one can define
zero or more view slots. Upon rendering time, those view slots are populated
with the viewlets that have been assigned to the slot.


The Difference betwen a Pagelet and a Portlet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's start with the properties the two share. Pagelets and portlets are
designed to be parts of a view; they are specialized viewlets. In the Zope
world the difference is commonly seen as follows:

  * A pagelet of a view displays the underlying context.

  * A portlet of a view displays data from different contexts.

For example, the metadata pagelet displays the metadata of the underlying
context. A metadata portlet, on the other hand, could display the metadata of
all of the context's children (assuming the context is a container). In a
second example, a calendar pagelet displays the calendar data of a content
object that implements its own calendar, while a calendar portlet displays
global calendar data on different objects that may come from an utility.

The above definitions need to be altered slightly when talking in terms of
Zope 3, since the adaption mechanism used for looking up views hides the data
retrieval from the user. Thus, let's slightly reword the definitions:

  * A pagelet of a view operates on the underlying context.

  * A portlet of a view operates on the underlying or on a different context.

Rephrasing our examples, we have: The metadata pagelet displays the metadata
of the view context by adapting it to ``IMetadata``. The portlet, on the other
hand, adapts to a context independent of the underlying view context.

Therefore, a set of pagelets of the same type inside a particular views must
always display similar content, while a set of portlets of the same type can
provide a wide range of contents from very different parts of the site.


Usage
-----

This pagelet implementation supports pagelets of the first and second
definition, but portlets only of the first. In the following text we use the
term "pagelet" as defined in the second definition.

Pagelets are responsible for a piece of content in a view. They can be used to
provide additionally information about an object that is not fully relevant
for the view's functionality, but provides useful information and/or links to
the user. Pagelets are small, view-like components that are identified by the
following set of interfaces they are registered for:

  * Layer: The layer in which the pagelet will be used.

  * Content Type: The interface the context of the the view must provide. This
    is the ``for`` attribute of the view and pagelet directive.

  * View: The interface the view must provide. By default this is
    ``IBrowserView`` and the default is commonly not changed.

  * Slot: The instance of the slot in which this pagelet can be placed.

Inside a pagetemplate the pagelets of a particular slot can be retrieved using
the ``pagelets`` TALES namespace. The return value is a sequence of pagelet
objects that can simply be called. The pagelets are selected by the four
above-mentioned parameters and sorted by the weight of the pagelets::

  <div class="row">
    <tal:repeat="pagelet pagelets:path.to.Slot">
      <tal:block replace="structure pagelet" />
    </tal:repeat>
  </div>


An Example
----------

Before we even start demonstrating the template, we need to register the
`pagelets` TALES namespace:

  >>> from zope.app.pagetemplate import metaconfigure
  >>> from zope.app.pagelet import tales
  >>> metaconfigure.registerType('pagelets', tales.TALESPageletsExpression)

The first task will be to create a slot that we can use in a pagetemplate. A
slot is simply an interface that simply needs to provide ``IPageletSlot``. The
interface is then registered as a utility providing the interface.

  >>> import zope.interface
  >>> class IDemoSlot(zope.interface.Interface):
  ...     '''A slot for demonstration purposes.'''

  >>> from zope.app.pagelet import interfaces
  >>> zope.interface.directlyProvides(IDemoSlot, interfaces.IPageletSlot)

  >>> import zope.component
  >>> zope.component.provideUtility(IDemoSlot, interfaces.IPageletSlot,
  ...                               'DemoSlot')

The argument to the slot class is commonly used for documentations. Next we
can create pagelets for this Now we can create a page template that uses this
slot object to define a slot in the template:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()

  >>> zpt_filename = os.path.join(temp_dir, 'template.pt')
  >>> open(zpt_filename, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>Pagelet Demo</h1>
  ...     <div class="left-column">
  ...       <div class="column-item"
  ...            tal:repeat="pagelet pagelets:DemoSlot">
  ...         <tal:block replace="structure pagelet" />
  ...       </div>
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')

Now that the template is created, we register the template as a browser page
view:

  >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
  >>> DemoPage = SimpleViewClass(zpt_filename, name='demo.html')

  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> zope.component.provideAdapter(
  ...     DemoPage,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...     name='demo.html')

In the following step we will create a couple of pagelets that are used in the
demo page. Pagelets are really views, except that they additionally adapt
their view and slot. The first pagelet is a minimalistic implementation:

  >>> from zope.app.publisher.browser import BrowserView
  >>> class Pagelet1(BrowserView):
  ...     weight = 0
  ...
  ...     def __init__(self, context, request, view, slot):
  ...         super(Pagelet1, self).__init__(context, request)
  ...
  ...     def __call__(self):
  ...         return u'<h3>Pagelet 1 Content</h3>'

  >>> from zope.security.checker import NamesChecker, defineChecker
  >>> pageletChecker = NamesChecker(('__call__', 'weight'))
  >>> defineChecker(Pagelet1, pageletChecker)

  >>> from zope.interface import Interface, providedBy
  >>> from zope.app.publisher.interfaces.browser import IBrowserView
  >>> zope.component.provideAdapter(
  ...     Pagelet1,
  ...     (Interface, IDefaultBrowserLayer, IBrowserView, IDemoSlot),
  ...     interfaces.IPagelet,
  ...     name='pagelet1')

Let's now register a more typical pagelet. We first create a template:

  >>> plt_filename = os.path.join(temp_dir, 'pagelet2.pt')
  >>> open(plt_filename, 'w').write('''
  ...         <div class="box">
  ...           <tal:block replace="pagelet/title" />
  ...         </div>
  ... ''')

  >>> class Pagelet2Base(object):
  ...     def title(self):
  ...         return 'Pagelet 2 Content'

As you can see, the pagelet Python class is known as ``pagelet``, while the
view class is still available as ``view``. Next we build and register the
pagelet using a special helper function:

  >>> from zope.app.pagelet import pagelet
  >>> Pagelet2 = pagelet.SimplePageletClass(
  ...     plt_filename, bases=(Pagelet2Base,), name='pagelet2', weight=1)

  >>> defineChecker(Pagelet2, pageletChecker)

  >>> zope.component.provideAdapter(
  ...     Pagelet2,
  ...     (Interface, IDefaultBrowserLayer, IBrowserView, IDemoSlot),
  ...     interfaces.IPagelet,
  ...     name='pagelet2')

Now all the setup is completed. Let's create a content object:

  >>> class Content(object):
  ...     zope.interface.implements(zope.interface.Interface)

  >>> content = Content()

and finally, we look up the view and render it:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> view = zope.component.getMultiAdapter((content, request),
  ...                                       name='demo.html')
  >>> print view().strip()
  <html>
    <body>
      <h1>Pagelet Demo</h1>
      <div class="left-column">
        <div class="column-item">
          <h3>Pagelet 1 Content</h3>
        </div>
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Pagelet 2 Content
          </div>
  <BLANKLINE>
        </div>
      </div>
    </body>
  </html>

Note that if we turn the weight around,

  >>> Pagelet1.weight = 1
  >>> Pagelet2._weight = 0

the order of the left column in the page template shoudl change:

  >>> print view().strip()
  <html>
    <body>
      <h1>Pagelet Demo</h1>
      <div class="left-column">
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Pagelet 2 Content
          </div>
  <BLANKLINE>
        </div>
        <div class="column-item">
          <h3>Pagelet 1 Content</h3>
        </div>
      </div>
    </body>
  </html>


Looking up a pagelet by name
----------------------------

In some cases you want to be able to look up a particular pagelet for a slot,
given a context and a view. For this use case, you can simply use a second
TALES namespace called ``pagelet`` that selects the pagelet using the
expression ``<path to slot>/<pagelet name>``.

  >>> metaconfigure.registerType('pagelet', tales.TALESPageletExpression)

Since everything else is already setup, we can simply register a new view:

  >>> zpt_filename2 = os.path.join(temp_dir, 'template2.pt')
  >>> open(zpt_filename2, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>Pagelet Demo</h1>
  ...     <div class="left-column">
  ...       <div class="column-item">
  ...         <tal:block replace="structure pagelet:DemoSlot/pagelet1" />
  ...       </div>
  ...     </div>
  ...   </body>
  ... </html>
  ... ''')

  >>> DemoPage2 = SimpleViewClass(zpt_filename2, name='demo2.html')
  >>> zope.component.provideAdapter(
  ...     DemoPage2,
  ...     (zope.interface.Interface, IDefaultBrowserLayer),
  ...     zope.interface.Interface,
  ...     name='demo2.html')

  >>> view = zope.component.getMultiAdapter((content, request),
  ...                                       name='demo2.html')
  >>> print view().strip()
  <html>
    <body>
      <h1>Pagelet Demo</h1>
      <div class="left-column">
        <div class="column-item">
          <h3>Pagelet 1 Content</h3>
        </div>
      </div>
    </body>
  </html>

Note that this namespace returns the rendered pagelet and not the pagelet
view, like the ``pagelets`` TALES namespace.
