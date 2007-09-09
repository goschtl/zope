=====================
View Reference Widget
=====================

The following example shows a ViewReferenceWidget:

  >>> import zope.interface
  >>> from z3c.reference.browser.widget import ViewReferenceWidget
  >>> from z3c.reference.schema import ViewReferenceField

At first we need an interface for the context our widget used for. The
`ìntro`` filed defines a settingName which is used by the widget to
get information about which edit form for the reference should
be used.

  >>> class IPage(zope.interface.Interface):
  ...     """Interface for a page."""
  ...
  ...     intro = ViewReferenceField(title=u'Intro',
  ...                                description=u'A intro text',
  ...                                settingName=u'introRefs')

Let's create an IPage implementation.

  >>> class Page(object):
  ...
  ...     zope.interface.implements(IPage)
  ...
  ...     def __init__(self, name):
  ...         self.__name__ = name

Let's create a page:

  >>> page = Page('Intro')
  >>> page.__parent__ = site

Now let's setup a enviroment for use the widget like in a real application::

  >>> from zope.app.testing import ztapi
  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.reference.interfaces import IViewReferenceField
  >>> from z3c.reference.schema import ViewReferenceField
  >>> from zope.app.form.interfaces import IInputWidget

Let's define a request and...

  >>> request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl')

let's initialize a ViewReferenceWidget with the right attributes::

  >>> field = IPage['intro']
  >>> boundField = field.bind(page)
  >>> widget = ViewReferenceWidget(boundField, request)

Now let's see how such a widget looks like if we render it with no value.

  >>> print widget()
  <a class="popupwindow" href="http://127.0.0.1/Intro/viewReferenceEditor.html?target=&amp;settingName=introRefs&amp;name=field.intro"
  id="field.intro.tag" name="field.intro" onclick="" title="Undefined"
  rel="window">Undefined</a>
  <BLANKLINE>
  <input class="hiddenType" id="field.intro.target" name="field.intro.target"
         type="hidden" value="" rel="window" />
  <input class="hiddenType" id="field.intro.formData"
         name="field.intro.formData" type="hidden" value="" rel="window" />
  <BLANKLINE>

If we store a empty request/form we will get the following error::

  >>> widget.applyChanges(page)
  Traceback (most recent call last):
  ...
  MissingInputError: ('field.intro', u'Intro', None)


Before we can store a view reference, we need at least another object which 
our page can reference. Let's create a simple text object::

  >>> class IText(zope.interface.Interface):
  ...     """Interface for a text object."""

  >>> class Text(object):
  ...
  ...     zope.interface.implements(IText)

  >>> text = Text()
  >>> text.__parent__ = site
  >>> text.__name__ = 'text'

Register the object in the intids util:

  >>> from zope.app.intid.interfaces import IIntIds
  >>> intids = zope.component.getUtility(IIntIds)
  >>> oid = intids.register(text)

Let us assign the text object here, so we can look at what the widget
renders if a target is defined.

  >>> from z3c.reference.reference import ViewReference
  >>> vr = ViewReference()
  >>> vr.target = text
  >>> page.intro = vr

  >>> field = IPage['intro']
  >>> boundField = field.bind(page)
  >>> request = TestRequest()
  >>> widget = ViewReferenceWidget(boundField, request)
  >>> widget.setRenderedValue(page.intro)
  >>> print widget()
  Traceback (most recent call last):
  ...
  ComponentLookupError: ((<Text object at ...>,
  <zope.publisher.browser.TestRequest instance URL=http://127.0.0.1>),
  <InterfaceClass z3c.reference.interfaces.IViewReferenceEditor>, u'introRefs')

Ups, we get an Error. We need a editor form for the given settings for
the target object. Let's create one that edits basic dublin core data.

  >>> from zope.formlib import form
  >>> from zope.dublincore.interfaces import IZopeDublinCore
  >>> from z3c.reference.interfaces import IViewReference
  >>> class IntroRefsEditForm(form.EditForm):
  ...     form_fields = form.Fields(IZopeDublinCore,
  ...     IViewReference).select('title', 'description', 'view')

And register it ...

  >>> from z3c.reference.interfaces import IViewReferenceEditor
  >>> from zope.publisher.interfaces.browser import IBrowserRequest
  >>> zope.component.provideAdapter(IntroRefsEditForm,
  ...     (zope.interface.Interface, IBrowserRequest),
  ...     IViewReferenceEditor,
  ...     name=u'introRefs')

We also need to register the widgets.

  >>> from zope.schema.interfaces import ITextLine, IText
  >>> from zope.app.form.browser import TextWidget, TextAreaWidget
  >>> from zope.app.form.browser.interfaces import ISimpleInputWidget
  >>> from zope.app.form.browser.interfaces import ITextBrowserWidget
  >>> zope.component.provideAdapter(TextWidget,
  ...     (ITextLine, IBrowserRequest), ITextBrowserWidget)
  >>> zope.component.provideAdapter(TextAreaWidget,
  ...     (IText, IBrowserRequest), ISimpleInputWidget)

So there is no formData for now, because we have no data on the reference.


  >>> print widget()
  <...name="field.intro.formData"
  ...value="form.title=&amp;form.view=&amp;form.description="...

Let us write some data to it.

  >>> IZopeDublinCore(vr).title = u"The DC Title"
  >>> IZopeDublinCore(vr).description = u"The DC Description"
  >>> print widget()
  <...
  value="form.title=The+DC+Title&amp;form.view=&amp;form.description=The+DC+Description"...

Now we can setup a test request and set the values for the widget:

  >>> formData = 'form.view=resized&form.title=New+Title&amp;form.description=New+Description'
  >>> form={'field.intro.target': oid,
  ...       'field.intro.formData': formData}

  >>> request = TestRequest(form=form)
  >>> widget = ViewReferenceWidget(boundField, request)
  >>> reference = widget._toFieldValue(form)
  >>> reference
  <z3c.reference.reference.ViewReference object at ...>

  >>> reference.target is text
  True

  >>> IZopeDublinCore(reference).title
  u'New Title'

  >>> IZopeDublinCore(reference).description
  u'New Description'

  >>> reference.view
  u'resized'

Let's save the new reference:

  >>> page.intro = reference


Let's register the reference in the intid util so we can compare after
update and check if we will get the same object wich is omportant.

  >>> refid = intids.register(reference)

Now do a update within the edit form:

  >>> form={'field.intro.target': oid,
  ...       'field.intro.view': 'w=16,h=9',
  ...       'field.intro.title': 'My same reference',
  ...       'field.intro.description': 'This is the same reference'}
  >>> request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl', form=form)
  >>> widget = ViewReferenceWidget(boundField, request)
  >>> same = widget._toFieldValue(form)
  >>> same
  <z3c.reference.reference.ViewReference object at ...>

And compare the reference within the same object we got:

  >>> reference is same
  True

  >>> refid == intids.getId(same)
  True


CropImageWidget
===============

  we need some resources
  
  >>> from zope import schema, interface
  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.reference.browser.widget import CropImageWidget
  >>> from zope.app.container.contained import Contained
  >>> class IContent(interface.Interface):
  ...     imageCropData = ViewReferenceField(title=u'image crop data',
  ...                                        required = False)
  >>> class Content(Contained):
  ...     pass
  >>> content = Content()
  >>> site['content'] = content

  >>> field = IContent['imageCropData']
  >>> field = field.bind(content)

  >>> request = TestRequest()
  >>> widget = CropImageWidget(field, request)
  >>> rendered = widget()
  >>> 'addVariable' in rendered
  True
  >>> 'http://127.0.0.1/content' in rendered
  True

