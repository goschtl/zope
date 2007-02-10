==============
Macro Provider
==============

This package provides a ZCML directive which allows you to register a macro 
deined in a template as a viewlet. Such a macro based viewlet acts 100% the 
same as a other viewlets. It could be very handy if you like to write a layout 
template in one page template and define selective parts as viewlets without 
to add any additional HTML. Let me show how this will look like:

The layout/master template can look like this:

  <!DOCTYPE ...>
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en"
        i18n:domain="z3c">
  <head>
  <tal:block replace="structure provider:ITitle">
    <metal:block define-macro="title">
      <title>The title</title>
    </metal:block>
  </tal:block>
  </head>
  <body tal:define="applicationURL request/getApplicationURL">
  <div id="content">
    <tal:block content="structure provider:pagelet">content</tal:block>
  </div>
  </div>
  </body>
  </html>

The tempalte aboce defines a ITitle provider which contains the definition 
for a macro in itself. Yo have to define a viewlet manager within the 
zope.viewlet ZCMl directive which provides ITitle as a viewlet manager.
After that you can register the template above as a layout template wthin
the z3c:layout ZCML directive like:

  <z3c:layout
      for="*"
      layer="z3c.skin.pagelet.IPageletBrowserSkin"
      template="template.pt"
      />

After that you can register the macro viewlet for the ITitle viewlet manager
like this:

  <z3c:macroViewlet
      for="*"
      template="template.pt"
      macro="title"
      manager="z3c.skin.pagelet.ITitle"
      layer="z3c.skin.pagelet.IPageletBrowserSkin"
      />

As you can see the ZCML configuration directive above uses ``title`` as the
macro attribute and uses ITitle as the viewlet manager. This will use the 
following part of the template.pt 

  <title>Pagelet skin</title>

and registers it as a viewlet. This viewlet get rendered in the ITitle 
provider. Ay you can see you can use a complete layout tempalte and use it
as it is. And here it comes, you can offer a included viewlet manager 
rendering the viewlet which can get overriden for other context or views etc.
You also can register more the one viewlet for the ITitle viewlet manager.
Wich of corse makes no sense in our special title tag example.

Let's show this in some tests. We start with creating a content object that 
is used as a view context later:

  >>> import zope.interface
  >>> import zope.component
  >>> from zope.publisher.interfaces.browser import IBrowserView
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> class Content(object):
  ...     zope.interface.implements(zope.interface.Interface)

  >>> content = Content()

We also create a temp dir for sample templates which we define later for 
testing:

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()

And we register security checker for the MacroViewlet class:

  >>> from zope.configuration.xmlconfig import XMLConfig
  >>> import zope.app.component
  >>> import z3c.macroviewlet
  >>> XMLConfig('meta.zcml', zope.app.component)()
  >>> XMLConfig('configure.zcml', z3c.macroviewlet)()


Layout template
---------------

We define a template including a macro definition and using a provider:

  >>> path = os.path.join(temp_dir, 'template.pt')
  >>> open(path, 'w').write('''
  ... <html>
  ... <body>
  ... <head>
  ... <tal:block replace="structure provider:ITitle">
  ...   <metal:block define-macro="title">
  ...     <title>The title</title>
  ...   </metal:block>
  ... </tal:block>
  ... </head>
  ... <body tal:define="applicationURL request/getApplicationURL">
  ...   content
  ... </body>
  ... </html>
  ... ''')

Let's register a view class using the view template:

  >>> import zope.interface
  >>> from zope.app.pagetemplate import viewpagetemplatefile
  >>> from zope.publisher.interfaces.browser import IBrowserView
  >>> class View(object):
  ...     zope.interface.implements(IBrowserView)
  ...     def __init__(self, context, request):
  ...        self.context = context
  ...        self.request = request
  ...     def __call__(self):
  ...         return viewpagetemplatefile.ViewPageTemplateFile(path)(self)

Let's prepare the view.

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> view = View(content, request)

Let's define the viewlet manager ``ITitle``:

  >>> from zope.viewlet.interfaces import IViewletManager
  >>> from zope.viewlet.manager import ViewletManager
  >>> class ITitle(IViewletManager):
  ...     """Viewlet manager located in the title tag."""

  >>> title = ViewletManager('title', ITitle)

Let's register the viewlet manager:

  >>> from zope.viewlet.interfaces import IViewletManager
  >>> manager = zope.component.provideAdapter(
  ...     title,
  ...     (zope.interface.Interface, TestRequest, IBrowserView),
  ...     IViewletManager, 
  ...     name='ITitle')


MacroViewlet
------------

Before we register the macro viewlet, we check the rendered page without any
registered macro viewlet:

  >>> print view()
  <html>
  <body>
  <head>
  </head>
  <body>
    content
  </body>
  </body></html>

As you can see there is no title rendered. Now we can define the macro 
viewlet...

  >>> from zope.app.pagetemplate import viewpagetemplatefile
  >>> from z3c.macroviewlet import zcml
  >>> macroViewlet = zcml.MacroViewletFactory(path, 'title', 'text/html')

and register them as adapter:

  >>> from zope.viewlet.interfaces import IViewlet
  >>> zope.component.provideAdapter(
  ...     macroViewlet,
  ...     (zope.interface.Interface, IDefaultBrowserLayer, IBrowserView, 
  ...      ITitle),
  ...     IViewlet,
  ...     name='title')

Now we are ready to test it again:

  >>> print view()
  <html>
  <body>
  <head>
      <title>The title</title>
  </head>
  <body>
    content
  </body>
  </body></html>

As you can see, the title get rendered as a viewlet into the ITitle provider.

Cleanup
-------

  >>> import shutil
  >>> shutil.rmtree(temp_dir)

