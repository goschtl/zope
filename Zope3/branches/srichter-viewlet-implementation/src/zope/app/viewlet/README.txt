========
Viewlets
========

This package provides a framework to develop componentized Web GUI
applications. Instead of describing the content of a page using a single
template or static system of templates and METAL macros, regions (called
regions) can be defined and are filled dynamically with content based on the
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
                          |* a view is composed of regions
                      ____v____
                     |          |
                     | ViewRegion |
                     |__________|
                          |
                          |
                          |* a region contains a list of viewlets
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
        | Viewlet |               | Portlet |
        |_________|               |_________|

Natively, Zope 3 allows us to associate one or more views to a given
object. Those views are either registered for the provided interfaces of the
object or the object itself. In a view, usually a template, one can define
zero or more view regions. Upon rendering time, those view regions are populated
with the viewlets that have been assigned to the region.


The Difference betwen a Viewlet and a Portlet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's start with the properties the two share. Viewlets and portlets are
designed to be parts of a view; they are specialized viewlets. In the Zope
world the difference is commonly seen as follows:

  * A viewlet of a view displays the underlying context.

  * A portlet of a view displays data from different contexts.

For example, the metadata viewlet displays the metadata of the underlying
context. A metadata portlet, on the other hand, could display the metadata of
all of the context's children (assuming the context is a container). In a
second example, a calendar viewlet displays the calendar data of a content
object that implements its own calendar, while a calendar portlet displays
global calendar data on different objects that may come from an utility.

The above definitions need to be altered slightly when talking in terms of
Zope 3, since the adaption mechanism used for looking up views hides the data
retrieval from the user. Thus, let's slightly reword the definitions:

  * A viewlet of a view operates on the underlying context.

  * A portlet of a view operates on the underlying or on a different context.

Rephrasing our examples, we have: The metadata viewlet displays the metadata
of the view context by adapting it to ``IMetadata``. The portlet, on the other
hand, adapts to a context independent of the underlying view context.

Therefore, a set of viewlets of the same type inside a particular views must
always display similar content, while a set of portlets of the same type can
provide a wide range of contents from very different parts of the site.


Usage
-----

This viewlet implementation supports viewlets of the first and second
definition, but portlets only of the first. In the following text we use the
term "viewlet" as defined in the second definition.

Viewlets are responsible for a piece of content in a view. They can be used to
provide additionally information about an object that is not fully relevant
for the view's functionality, but provides useful information and/or links to
the user. Viewlets are small, view-like components that are identified by the
following set of interfaces they are registered for:

  * Layer: The layer in which the viewlet will be used.

  * Content Type: The interface the context of the the view must provide. This
    is the ``for`` attribute of the view and viewlet directive.

  * View: The interface the view must provide. By default this is
    ``IBrowserView`` and the default is commonly not changed.

  * Region: The instance of the region in which this viewlet can be placed.

Inside a pagetemplate the viewlets of a particular region can be retrieved using
the ``viewlets`` TALES namespace. The return value is a sequence of viewlet
objects that can simply be called. The viewlets are selected by the four
above-mentioned parameters and sorted by the weight of the viewlets::

  <div class="row">
    <tal:repeat="viewlet viewlets:path.to.Region">
      <tal:block replace="structure viewlet" />
    </tal:repeat>
  </div>


An Example
----------

Before we even start demonstrating the template, we need to register the
`viewlets` TALES namespace:

  >>> from zope.app.pagetemplate import metaconfigure
  >>> from zope.app.viewlet import tales
  >>> metaconfigure.registerType('viewlets', tales.TALESViewletsExpression)

The first task will be to create a region that we can use in a pagetemplate. A
region is simply an interface that simply needs to provide ``IViewletRegion``. The
interface is then registered as a utility providing the interface.

  >>> import zope.interface
  >>> class IDemoRegion(zope.interface.Interface):
  ...     '''A region for demonstration purposes.'''

  >>> from zope.app.viewlet import interfaces
  >>> zope.interface.directlyProvides(IDemoRegion, interfaces.IViewletRegion)

  >>> import zope.component
  >>> zope.component.provideUtility(IDemoRegion, interfaces.IViewletRegion,
  ...                               'DemoRegion')

The argument to the region class is commonly used for documentations. Next we
can create viewlets for this Now we can create a page template that uses this
region object to define a region in the template:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()

  >>> zpt_filename = os.path.join(temp_dir, 'template.pt')
  >>> open(zpt_filename, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>Viewlet Demo</h1>
  ...     <div class="left-column">
  ...       <div class="column-item"
  ...            tal:repeat="viewlet viewlets:DemoRegion">
  ...         <tal:block replace="structure viewlet" />
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

In the following step we will create a couple of viewlets that are used in the
demo page. Viewlets are really views, except that they additionally adapt
their view and region. The first viewlet is a minimalistic implementation:

  >>> from zope.app.publisher.browser import BrowserView
  >>> class Viewlet1(BrowserView):
  ...     weight = 0
  ...
  ...     def __init__(self, context, request, view, region):
  ...         super(Viewlet1, self).__init__(context, request)
  ...
  ...     def __call__(self):
  ...         return u'<h3>Viewlet 1 Content</h3>'

  >>> from zope.security.checker import NamesChecker, defineChecker
  >>> viewletChecker = NamesChecker(('__call__', 'weight'))
  >>> defineChecker(Viewlet1, viewletChecker)

  >>> from zope.interface import Interface, providedBy
  >>> from zope.app.publisher.interfaces.browser import IBrowserView
  >>> zope.component.provideAdapter(
  ...     Viewlet1,
  ...     (Interface, IDefaultBrowserLayer, IBrowserView, IDemoRegion),
  ...     interfaces.IViewlet,
  ...     name='viewlet1')

Let's now register a more typical viewlet. We first create a template:

  >>> plt_filename = os.path.join(temp_dir, 'viewlet2.pt')
  >>> open(plt_filename, 'w').write('''
  ...         <div class="box">
  ...           <tal:block replace="viewlet/title" />
  ...         </div>
  ... ''')

  >>> class Viewlet2Base(object):
  ...     def title(self):
  ...         return 'Viewlet 2 Content'

As you can see, the viewlet Python class is known as ``viewlet``, while the
view class is still available as ``view``. Next we build and register the
viewlet using a special helper function:

  >>> from zope.app.viewlet import viewlet
  >>> Viewlet2 = viewlet.SimpleViewletClass(
  ...     plt_filename, bases=(Viewlet2Base,), name='viewlet2', weight=1)

  >>> defineChecker(Viewlet2, viewletChecker)

  >>> zope.component.provideAdapter(
  ...     Viewlet2,
  ...     (Interface, IDefaultBrowserLayer, IBrowserView, IDemoRegion),
  ...     interfaces.IViewlet,
  ...     name='viewlet2')

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
      <h1>Viewlet Demo</h1>
      <div class="left-column">
        <div class="column-item">
          <h3>Viewlet 1 Content</h3>
        </div>
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Viewlet 2 Content
          </div>
  <BLANKLINE>
        </div>
      </div>
    </body>
  </html>

Note that if we turn the weight around,

  >>> Viewlet1.weight = 1
  >>> Viewlet2._weight = 0

the order of the left column in the page template shoudl change:

  >>> print view().strip()
  <html>
    <body>
      <h1>Viewlet Demo</h1>
      <div class="left-column">
        <div class="column-item">
  <BLANKLINE>
          <div class="box">
            Viewlet 2 Content
          </div>
  <BLANKLINE>
        </div>
        <div class="column-item">
          <h3>Viewlet 1 Content</h3>
        </div>
      </div>
    </body>
  </html>


Looking up a viewlet by name
----------------------------

In some cases you want to be able to look up a particular viewlet for a region,
given a context and a view. For this use case, you can simply use a second
TALES namespace called ``viewlet`` that selects the viewlet using the
expression ``<path to region>/<viewlet name>``.

  >>> metaconfigure.registerType('viewlet', tales.TALESViewletExpression)

Since everything else is already setup, we can simply register a new view:

  >>> zpt_filename2 = os.path.join(temp_dir, 'template2.pt')
  >>> open(zpt_filename2, 'w').write('''
  ... <html>
  ...   <body>
  ...     <h1>Viewlet Demo</h1>
  ...     <div class="left-column">
  ...       <div class="column-item">
  ...         <tal:block replace="structure viewlet:DemoRegion/viewlet1" />
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
      <h1>Viewlet Demo</h1>
      <div class="left-column">
        <div class="column-item">
          <h3>Viewlet 1 Content</h3>
        </div>
      </div>
    </body>
  </html>

Note that this namespace returns the rendered viewlet and not the viewlet
view, like the ``viewlets`` TALES namespace.
