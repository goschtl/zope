Walk-through
============

Layouts and regions
-------------------

Let's begin by instantiating a layout. We'll do this manually for the
sake of this demonstration; usually this is done using the included
ZCML-directive <browser:layout>.

    >>> from z3c.layout.model import Layout
    
    >>> layout = Layout(
    ...     "test", "%s/templates/default/index.html" % test_path, "test")

Register resource directory.
    
    >>> import zope.configuration.config as config
    >>> context = config.ConfigurationMachine()
    
    >>> from zope.app.publisher.browser import resourcemeta
    >>> resourcemeta.resourceDirectory(
    ...     context, "test", "%s/templates/default" % test_path)
    >>> context.execute_actions()
    
Layouts are made dynamic by defining one or more regions. They are
mapped to HTML locations using an xpath-expression and an insertion
mode, which is one of "replace", "append", "prepend", "before" or
"after".

Regions can specify the name of a content provider directly or it may
rely on adaptation to yield a content provider component. We'll
investigate both of these approaches:

    >>> from z3c.layout.model import Region

First we define a title region where we directly specify the name of a
content provider.

    >>> title = Region("title", ".//title", title=u"Title", provider="title")

Then a content region where we leave it the content provider to
component adaptation.
    
    >>> content = Region("content", ".//div", "Content")

To register them with the layout we simply add them.

    >>> layout.regions.add(title)
    >>> layout.regions.add(content)

Let's define a context class.
    
    >>> class MockContext(object):
    ...     interface.implements(interface.Interface)

We need to provide a general adapter that can provide content
providers for regions that do not specify them directly. As an
example, we'll define an adapter that simply tries to lookup a content
provider with the same name as the region.

    >>> from z3c.layout.interfaces import IContentProviderFactory

    >>> class EponymousContentProviderFactory(object):
    ...     interface.implements(IContentProviderFactory)
    ...
    ...     def __init__(self, region):
    ...         self.region = region
    ...
    ...     def __call__(self, context, request, view):
    ...         name = self.region.name
    ...         return component.getMultiAdapter(
    ...            (view.context, request, view), IContentProvider, name)

    >>> from z3c.layout.interfaces import IRegion
    
    >>> component.provideAdapter(
    ...     EponymousContentProviderFactory, (IRegion,))
    
Rendering
---------

Before we can render the layout, we need to register content providers
for the two regions. We'll use a mock class for demonstration.

    >>> from zope.contentprovider.interfaces import IContentProvider
    
    >>> class MockContentProvider(object):
    ...     interface.implements(IContentProvider)
    ...     
    ...     __name__ = u""
    ...
    ...     def __init__(self, *args):
    ...         pass
    ...
    ...     def update(self):
    ...         pass
    ...
    ...     def render(self):
    ...         return self.__name__
    ...
    ...     def __repr__(self):
    ...         return "<MockContentProvider '%s'>" % self.__name__
    
    >>> from zope.publisher.interfaces.browser import IBrowserRequest
    >>> from zope.publisher.interfaces.browser import IBrowserView

    >>> component.provideAdapter(
    ...     MockContentProvider, (MockContext, IBrowserRequest, IBrowserView),
    ...     name="title")

    >>> component.provideAdapter(
    ...     MockContentProvider, (MockContext, IBrowserRequest, IBrowserView),
    ...     name="content")

Let's instantiate the layout browser-view. We must define a context
and set up a request.

    >>> from zope.publisher.browser import TestRequest
    
    >>> context = MockContext()
    >>> request = TestRequest()

We need to have the request be annotatable.

    >>> from zope.annotation.attribute import AttributeAnnotations
    >>> component.provideAdapter(
    ...     AttributeAnnotations, (TestRequest,))
    
The view expects the context to adapt to ``ILayout``.
    
    >>> from z3c.layout.interfaces import ILayout
    >>> component.provideAdapter(
    ...     lambda context: layout, (MockContext,), ILayout)

    >>> from z3c.layout.browser.layout import LayoutView
    >>> view = LayoutView(context, request)

Verify that the layout view is able to get to these providers.
    
    >>> view.mapping
    {'content':
     (<Region 'content' .//div (replace) None>, <MockContentProvider 'content'>),
     'title':
     (<Region 'title' .//title (replace) 'title'>, <MockContentProvider 'title'>)}

Now for the actual output.

    >>> print view()
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
    <html>
    <head>
    <link rel="stylesheet" href="test/main.css" type="text/css" media="screen">
    <title>title</title>
    </head>
    <body>
        <div id="content">content</div>
      </body>
    </html>

Transforms
----------

To support special cases where you need to use Python to transform the
static HTML document at compile time, one or more transforms may be
defined.

    >>> from z3c.layout.model import Transform

Let's add a transform that adds a language setting to the <html>-tag.

    >>> def set_language(node):
    ...     node.attrib["lang"] = "en"
    
    >>> layout.transforms.add(
    ...    Transform(set_language))

    >>> layout.parse().getroot().attrib["lang"]
    'en'

And another transform that assigns a class to the <body>-tag.

    >>> def set_class(node, value):
    ...     node.attrib["class"] = value
    
    >>> layout.transforms.add(
    ...    Transform(lambda body: set_class(body, "front-page"), ".//body"))

    >>> layout.parse().xpath('.//body')[0].attrib["class"]
    'front-page'
