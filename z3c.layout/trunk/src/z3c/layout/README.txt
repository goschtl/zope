Walk-through
============

A layout is essentially an HTML-document with zero or more region
definitions.

Let's begin by instantiating a layout. We'll do this manually for the
sake of this demonstration; usually this is done using the
ZCML-directive <browser:layout>, which is available with this package.

    >>> from z3c.layout.layout import Layout
    >>> layout = Layout(
    ...     "Testlayout",
    ...     "test",
    ...     "%s/templates/default/index.html" % test_path,
    ...     "index.jpg")

We need register this layout as a utility to make it available for the
rendering machinery.

    >>> from z3c.layout.interfaces import ILayout
    >>> component.provideUtility(layout, ILayout, name="testlayout")

Regions
-------

A region is the interior of an element in the template as located by
an xpath-expression. Regions are named and may optionally be given a
title.

    >>> from z3c.layout.regions import Region

We'll define two regions.

    >>> logo = Region("logo", ".//p", "The Logo Region")
    >>> content = Region("content", ".//div", "The Content Region")

To add them to the layout we simply append them to the list of
regions.

    >>> layout.regions.append(logo)
    >>> layout.regions.append(content)

Region content providers
------------------------

Regions are rendered by content providers. When rendering a page, a
layout assignment dictates which providers are to be used for
rendering which regions.

    >>> from z3c.layout.interfaces import ILayoutAssignment

A layout assignment defines the active layout and has information on
how to render each region. This is defined in the provider map:

    >>> class LayoutAssignment(object):
    ...     def __init__(self, name, provider_map):
    ...         self.name = name
    ...         self.provider_map = provider_map

Let's set up an assignment for our two regions.
    
    >>> assignment = LayoutAssignment('testlayout', {
    ...     'logo': 'logo_provider',
    ...     'content': 'content_provider'})

A layout is rendered in some context, typically a page. We'll provide
this layout assignment for all such pages.

    >>> class MockPage(object):
    ...     interface.implements(interface.Interface)
    
    >>> component.provideAdapter(
    ...     lambda page: assignment, (MockPage,), ILayoutAssignment)
    
We proceed by setting up content providers that render the
regions. This follows the standard content provider interface.

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

    >>> from z3c.layout.interfaces import IRegion

    >>> component.provideAdapter(
    ...     MockContentProvider, (IRegion, IBrowserRequest, IBrowserView),
    ...     name="logo_provider")

    >>> component.provideAdapter(
    ...     MockContentProvider, (IRegion, IBrowserRequest, IBrowserView),
    ...     name="content_provider")

Rendering the layout
--------------------
    
The layout is rendered by a specialized view.
    
    >>> from zope.publisher.browser import TestRequest
    >>> page = MockPage()
    >>> request = TestRequest()

    >>> from z3c.layout.browser.layout import LayoutView
    >>> view = LayoutView(page, request)

Verify that the layout view is able to get to these providers.
    
    >>> list(view._get_region_content_providers())
    [(<Region 'logo'>, <MockContentProvider 'logo'>),
     (<Region 'content'>, <MockContentProvider 'content'>)]

    >>> assignment.provider_map['logo'] = 'non_existing_logo_provider'

Even if a provider map is registered, we might not be able to look
them up. Missing components will be silently ignored.

    >>> list(view._get_region_content_providers())
    [(<Region 'content'>, <MockContentProvider 'content'>)]

Let's restore the assignment to the correct logo provider before
proceeding.

    >>> assignment.provider_map['logo'] = 'logo_provider'
    
Let's try rendering the page. We expect the interior of the two
regions we've defined to be replaced by the output of the (dummy)
region content providers.
     
    >>> print view()
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
    <html>
    <head><link rel="stylesheet" href="++resource++test/main.css" type="text/css" media="screen"></head>
    <body>
        <p>logo</p>
        <div id="content">content</div>
      </body>
    </html>

Tree content providers
----------------------

Layouts may be augmented with tree content providers that insert their
content into the element tree before it's serialized and returned.

    >>> from z3c.layout.browser.interfaces import ITreeContentProvider
    >>> import lxml.html
    
    >>> class MockTreeContentProvider(MockContentProvider):
    ...     interface.implements(ITreeContentProvider)
    ...
    ...     def insert(self, tree):
    ...         body = tree.find('.//body')
    ...         body.append(lxml.html.fromstring(self.render()))
    ...
    ...     def render(self):
    ...         return u"<span>Hello World!</span>"
    
    >>> component.provideAdapter(
    ...     MockTreeContentProvider,
    ...     (MockPage, IBrowserRequest, IBrowserView),
    ...     IContentProvider)

    >>> print view()
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
    <html>
    <head><link rel="stylesheet" href="++resource++test/main.css" type="text/css" media="screen"></head>
    <body>
        <p>logo</p>
        <div id="content">content</div>
      <span>Hello World!</span>
    </body>
    </html>
