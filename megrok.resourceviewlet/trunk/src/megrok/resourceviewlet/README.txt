======================
megrok.resourceviewlet
======================

`megrok.resourceviewlet` is a package meant to include resources
using layer, context and view discriminations.


Setup
=====

Let's import and init the necessary work environment::

  >>> import grokcore.component as grok
  >>> from grokcore import view, viewlet
  >>> from zope.app.wsgi.testlayer import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False


Library
=======

We first declare a resource. We'll include it in our page::

  >>> from fanstatic import Resource, Library
  >>> myLibrary = Library('test_library', 'ftests/resources')
  >>> Thing = Resource(myLibrary, 'thing.js')

This step is done by an entry point. For the testing, we do it by hand::

  >>> from zope.fanstatic.zcml import create_factory
  >>> from zope.component import getGlobalSiteManager
  >>> from zope.publisher.interfaces.browser import IBrowserRequest
  >>> from zope.interface import Interface

  >>> resource_factory = create_factory(myLibrary)
  >>> getGlobalSiteManager().registerAdapter(
  ...      resource_factory, (IBrowserRequest,), Interface, myLibrary.name)


Components
==========

To demonstrate our resource viewlet, we first need a page to
render. This page contains a content provider named 'resources'::

  >>> from zope.interface import Interface

  >>> class Index(view.View):
  ...   view.require("zope.Public")
  ...   view.context(Interface)
  ...
  ...   template = view.PageTemplate("""<html><head>
  ...     <tal:resources replace='provider:resources' />
  ...   </head></html>""")

  >>> grok.testing.grok_component('index', Index)
  True


Manager
-------

We now register a content provider named 'resources'. It will be a
ResourcesManager. An ResourcesManager is a component
dedicated in rendering ResourceViewlets::

  >>> from megrok.resourceviewlet import ResourcesManager

  >>> class Resources(ResourcesManager):
  ...   viewlet.context(Interface)
 
  >>> grok.testing.grok_component('resources', Resources)
  True


Viewlet
-------

Now, we register a ResourceViewlet, including our resource. The
declaration is very straightforward::

  >>> from megrok.resourceviewlet import ResourceViewlet

  >>> class SomeViewlet(ResourceViewlet):
  ...   viewlet.context(Interface)
  ...   resources = [Thing]

  >>> grok.testing.grok_component('viewlet', SomeViewlet)
  True

By default, a ResourceViewlet is registered for an instance of
ResourcesManager. Most of the time, a page contains only one of
these content providers. If it's not the case, make sure to provide
your own `viewletmanager` directive value.


Rendering
=========

Rendering our page should render the ResourcesManager and
therefore, include our resource::

  >>> browser.open('http://localhost/@@index')
  >>> print browser.contents
  <html><head>
    <script type="text/javascript"
     src="http://localhost/fanstatic/test_library/thing.js"></script>
  </head></html>

It works ! Enjoy.
