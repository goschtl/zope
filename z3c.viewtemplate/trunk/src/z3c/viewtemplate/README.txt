============
ViewTemplate
============

This package allows us to separate the registration of the view code and the
view templates.

Why is this a good thing?

While developing customizable applications that require us to develop multiple
customer UIs for one particular application, we noticed there is a fine but
clear distinction between skins and layers. Layers contain the logic to
prepare data for presentation output, namely the view classes. Skins, on the
other hand contain the resources to generate the UI, for example templates,
images and CSS files.

The problem of the existing infrastructure is that code, template and layer
are all hardlinked in one zcml configuration directive of the view component
-- page, content provider, viewlet. This package separates this triplet --
code, template, layer -- into two pairs, code/layer and template/skin. No
additional components are introduced, since skins and layers are physically
the same components.

Before we can setup a view component using this new method, we have to first
create a template ...

  >>> import os, tempfile
  >>> temp_dir = tempfile.mkdtemp()
  >>> template = os.path.join(temp_dir, 'demoTemplate.pt')
  >>> open(template, 'w').write('''<div>demo</div>''')

and the view code:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> from zope import interface
  >>> from z3c.viewtemplate.baseview import BaseView
  >>> class IMyView(interface.Interface):
  ...     pass
  >>> class MyView(BaseView):
  ...     interface.implements(IMyView)

  >>> view = MyView(root, request)

Since the template is not yet registered, rendering the view will fail:

  >>> print view()
  Traceback (most recent call last):
  ...
  ComponentLookupError: ......

Let's now register the template (commonly done using ZCML):

  >>> from zope import component
  >>> from zope.publisher.interfaces.browser import IDefaultBrowserLayer
  >>> from z3c.viewtemplate.zcml import TemplateFactory
  >>> from zope.pagetemplate.interfaces import IPageTemplate

The template factory allows us to create a ViewPageTeplateFile instance.

  >>> factory = TemplateFactory(template, None, 'text/html')

We register the factory on a view interface and a layer.

  >>> component.provideAdapter(factory,
  ...            (interface.Interface, IDefaultBrowserLayer),
  ...            IPageTemplate)
  >>> template = component.getMultiAdapter(
  ...               (view, request), IPageTemplate)
  >>> template
  <zope.app.pagetemplate.viewpagetemplatefile.ViewPageTemplateFile ...>

Now that we have a registered template for the default layer we can
call our view again. The view is a contentprovider so a
BeforeUpdateEvent is fired before its update method is called.

  >>> events = []
  >>> component.provideHandler(events.append, (None,))
  >>> print view()
  <div>demo</div>
  >>> events
  [<zope.contentprovider.interfaces.BeforeUpdateEvent object at ...>]

Now we register a new template on the specific interface of our view.

  >>> myTemplate = os.path.join(temp_dir, 'myViewTemplate.pt')
  >>> open(myTemplate, 'w').write('''<div>IMyView</div>''')
  >>> factory = TemplateFactory(myTemplate, None, 'text/html')
  >>> component.provideAdapter(factory,
  ...            (IMyView, IDefaultBrowserLayer),
  ...            IPageTemplate)
  >>> print view()
  <div>IMyView</div>

We can also render the view with debug flags set.

  >>> request.debug.sourceAnnotations = True
  >>> print view()
  <!--
  ==============================================================================
  .../myViewTemplate.pt
  ==============================================================================
  --><div>IMyView</div>
  >>> request.debug.sourceAnnotations = False

It is possible to provide the template directly.

We create a new template.

  >>> viewTemplate = os.path.join(temp_dir, 'viewTemplate.pt')
  >>> open(viewTemplate, 'w').write('''<div>view</div>''')

  >>> from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
  >>> class MyViewWithTemplate(BaseView):
  ...     interface.implements(IMyView)
  ...     template = ViewPageTemplateFile(viewTemplate)
  >>> templatedView = MyViewWithTemplate(root, request)

If we render this view we get the original template and not the registered
one.

  >>> print templatedView()
  <div>view</div>


Use of macros.

  >>> macroTemplate = os.path.join(temp_dir, 'macroTemplate.pt')
  >>> open(macroTemplate, 'w').write('''
  ...   <metal:block define-macro="macro1">
  ...     <div>macro1</div>
  ...   </metal:block>
  ...   <metal:block define-macro="macro2">
  ...   <div tal:content="options/foo">macro2</div>
  ...   </metal:block>
  ...   ''')

  >>> factory = TemplateFactory(macroTemplate, 'macro1', 'text/html')
  >>> print factory(view, request)()
  <div>macro1</div>

Since it is possible to pass options to the viewlet let's prove if this
is possible for macros as well:

  >>> factory = TemplateFactory(macroTemplate, 'macro2', 'text/html')
  >>> print factory(view, request)(foo='bar')
  <div>bar</div>


Why didn't we use named templates from the ``zope.formlib`` package?

While named templates allow us to separate the view code from the template
registration, they are not registrable for a particular layer making it
impossible to implement multiple skins using named templates.


Page Template
-------------

And for the simplest possible use we provide a RegisteredPageTemplate a la
ViewPageTemplateFile or NamedTemplate.

The RegisteredPageTemplate allows us to use the new template registration
system with all existing implementations such as `zope.formlib` and
`zope.viewlet`.

  >>> from z3c.viewtemplate.pagetemplate import RegisteredPageTemplate
  >>> class IMyUseOfView(interface.Interface):
  ...     pass
  >>> class UseOfRegisteredPageTemplate(object):
  ...     interface.implements(IMyUseOfView)
  ...
  ...     template = RegisteredPageTemplate()
  ...
  ...     def __init__(self, context, request):
  ...         self.context = context
  ...         self.request = request

By defining the "template" property as a "RegisteredPageTemplate" a lookup for
a registered template is done when it is called. Also notice that it is no
longer necessary to derive the view from BaseView!

  >>> simple = UseOfRegisteredPageTemplate(root, request)
  >>> print simple.template()
  <div>demo</div>

Because the demo template was registered for any ("None") interface we see the
demo template when rendering our new view. We register a new template
especially for the new view. Also not that the "macroTemplate" has been
created earlier in this test.

  >>> factory = TemplateFactory(macroTemplate, 'macro2', 'text/html')
  >>> component.provideAdapter(factory,
  ...            (IMyUseOfView, IDefaultBrowserLayer),
  ...            IPageTemplate)
  >>> print simple.template(foo='bar')
  <div>bar</div>

