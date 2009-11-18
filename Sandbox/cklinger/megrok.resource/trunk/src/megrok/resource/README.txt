===============
megrok.resource
===============

After many discussions on the mailinglist, on irc and the sprint in cologne
i started to work on a first prototype of megrok.resource.

megrok.resource is a combination of these packages:

 - hurry.resource
 - hurry.zoperesource
 - grokcore.view.ResourceDirectory
 - z3c.hashedresource (if our zope.app.publisher >= 3.8.2)


How does it work:
=================

Setup
-----

  >>> from zope.app.testing.functional import getRootFolder
  >>> from zope.app.component.site import SiteManagerContainer 
  >>> from zope.app.component.site import LocalSiteManager
  >>> from zope.app.component.hooks import setSite

  >>> class Application(SiteManagerContainer):
  ...     pass

  >>> root = getRootFolder()
  >>> root['myapp'] = Application()

Our application has to be a Site to access the right url for the inclusions

  >>> root['myapp'].setSiteManager(LocalSiteManager(root['myapp']))
  >>> setSite(root['myapp'])
  >>> root['myapp']
  <megrok.resource.ftests.Application object at ...>

Let's start with a Library. A Library is in the context of megrok.resource
a ResourceDirectory which holds a kind of different ResourceInclusions

  >>> from megrok.resource import Library, inclusion, include
  >>> import grokcore.view as view 
  >>> import grokcore.component as grok 

  >>> class MyStylesA(Library):
  ...    view.path('css')
  ...    grok.name('mystyles')
  ...
  ...    inclusion(name='myjs', file='a.js')  

  >>> grok.testing.grok_component('MyStylesA', MyStylesA)
  True
