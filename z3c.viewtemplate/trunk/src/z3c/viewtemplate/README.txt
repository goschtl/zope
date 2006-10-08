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

The problem of the existing infrastructure is that code, template and layer are all
hardlinked in one zcml configuration directive of the view component  -- page,
content provider, viewlet. This package separates this triplet -- code, template,
layer -- into two pairs, code/layer and template/skin. No additional
components are introduced, since skins and layers are physically the same
components.

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

Now that we have a registered template for the default layer we can call our
view again.

  >>> print view()
  <div>demo</div>

Now we register a new template on the specific interface of our view.

  >>> myTemplate = os.path.join(temp_dir, 'myViewTemplate.pt')
  >>> open(myTemplate, 'w').write('''<div>IMyView</div>''')
  >>> factory = TemplateFactory(myTemplate, None, 'text/html')
  >>> component.provideAdapter(factory,
  ...            (IMyView, IDefaultBrowserLayer),
  ...            IPageTemplate)
  >>> print view()
  <div>IMyView</div>

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
  ...     <div>macro2</div>
  ...   </metal:block>
  ...   ''')

  >>> factory = TemplateFactory(macroTemplate, 'macro1', 'text/html')
  >>> print factory(view, request)()
  <div>macro1</div>


Why didn't we use named templates from the ``zope.formlib`` package?

While named templates allow us to separate the view code from the template
registration, they are not registerable for a particular layer making it
impossible to implement multiple skins using named templates.


Page Template
-------------

And for the simplest possible use we provide a RegisteredPageTemplate a la
ViewPageTemplateFile or NamedTemplate.

The RegisteredPageTemplate allows us to use new template registration system
with all existing implementations such as `zope.formlib` and `zope.viewlet`.

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

  >>> simple = UseOfRegisteredPageTemplate(root, request)
  >>> print simple.template()
  <div>demo</div>

  >>> factory = TemplateFactory(macroTemplate, 'macro2', 'text/html')
  >>> component.provideAdapter(factory,
  ...            (IMyUseOfView, IDefaultBrowserLayer),
  ...            IPageTemplate)
  >>> print simple.template()
  <div>macro2</div>

