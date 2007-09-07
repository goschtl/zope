=====================
View Reference Widget
=====================

The following example shows a ViewReferenceWidget:

  >>> import zope.interface
  >>> from z3c.reference.browser.widget import ViewReferenceWidget
  >>> from z3c.reference.schema import ViewReferenceField

  >>> class IPage(zope.interface.Interface):
  ...     """Interface for a page."""
  ...
  ...     intro = ViewReferenceField(title=u'Intro',
  ...                                description=u'A intro text',
  ...                                settingName=u'')

Let's define the IPage object:

  >>> class Page(object):
  ...
  ...     zope.interface.implements(IPage)
  ...
  ...     def __init__(self, name):
  ...         self.name = name

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

Now let's see how such a widget looks like if we render them::

  >>> print widget() # doctest: +NORMALIZE_WHITESPACE
  <a class="popupwindow"
  href="http://127.0.0.1/viewReferenceEditor.html?name=field.intro&amp;target=&amp;settingName=&amp;view="
  id="field.intro.tag" name="field.intro" onclick="" title="Undefined"
  rel="window">Undefined</a><input class="hiddenType" id="field.intro.view"
  name="field.intro.view" type="hidden" value="" rel="window" /><input
  class="hiddenType" id="field.intro.target" name="field.intro.target"
  type="hidden" value="" rel="window" /><input class="hiddenType"
  id="field.intro.title" name="field.intro.title" type="hidden" value=""
  rel="window" /><input class="hiddenType" id="field.intro.description"
  name="field.intro.description" type="hidden" value="" rel="window" />

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

Register the object in the intids util:

  >>> from zope.app.intid.interfaces import IIntIds
  >>> intids = zope.component.getUtility(IIntIds)
  >>> oid = intids.register(text)

Now we can setup a test request and set the values for the widget:
  >>> form={'field.intro.target': oid,
  ...       'field.intro.view': 'ratio=16x9',
  ...       'field.intro.title': 'My reference',
  ...       'field.intro.description': 'This is a reference'}
  >>> request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl', form=form)
  >>> widget = ViewReferenceWidget(boundField, request)
  >>> reference = widget._toFieldValue(form)
  >>> reference
  <z3c.reference.reference.ViewReference object at ...>

  >>> reference.target is text
  True

  >>> reference.view
  u'ratio=16x9'

  >>> reference.title
  u'My reference'

  >>> reference.description
  u'This is a reference'

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
