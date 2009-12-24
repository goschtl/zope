======================
megrok.resourceviewlet
======================

`megrok.resourceviewlet`

Setup
=====

Let's import and init the necessary work environment::

  >>> import grokcore.component as grok
  >>> from grokcore import view, viewlet
  >>> from zope.testbrowser.testing import Browser

  >>> browser = Browser()
  >>> browser.handleErrors = False 


Library
=======

  >>> from megrok import resource
  >>> class SomeResource(resource.ResourceLibrary):
  ...     resource.path('ftests/resources')
  ...     resource.resource('thing.js')

  >>> grok.testing.grok_component('library', SomeResource)
  True


Components
==========

View
----

  >>> from zope.interface import Interface

  >>> class Index(view.View):
  ...   view.context(Interface)
  ...
  ...   template = view.PageTemplate("""<html><head>
  ...     <tal:resources replace='provider:resources' />
  ...   </head></html>""")

  >>> grok.testing.grok_component('index', Index)
  True


Manager
-------

  >>> from megrok.resourceviewlet import InclusionViewletManager

  >>> class Resources(InclusionViewletManager):
  ...   viewlet.context(Interface)
  ...   viewlet.view(Index)

  >>> grok.testing.grok_component('resources', Resources)
  True


Viewlet
-------

  >>> from megrok.resourceviewlet import ResourceViewlet

  >>> class SomeViewlet(ResourceViewlet):
  ...   viewlet.viewletmanager(Resources)
  ...   viewlet.context(Interface)
  ...   resources = [SomeResource]

  >>> grok.testing.grok_component('viewlet', SomeViewlet)
  True


Rendering
---------

  >>> browser.open('http://localhost/@@index')
  >>> print browser.contents
  <html><head>
    <script
      type="text/javascript"
      src="http://localhost/@@/++noop++.../someresource/thing.js"></script>
  </head></html>
