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

Now let's setup a enviroment for use the widget like in a real application::

  >>> from zope.app.testing import ztapi
  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.reference.interfaces import IViewReferenceField
  >>> from z3c.reference.schema import ViewReferenceField
  >>> from z3c.reference.browser.widget import ViewReferenceWidget
  >>> from zope.app.form.interfaces import IInputWidget

Let's define a request and...

  >>> request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl')

let's initialize a ViewReferenceWidget with the right attributes::

  >>> field = IPage['intro']
  >>> widget = ViewReferenceWidget(field, request)

Now let's see how such a widget looks like if we render them::

  >>> print widget()
  <a class="popupwindow" href="http://127.0.0.1/viewReferenceEditor.html"
     id="field.intro.tag" name="field.intro" onclick="" title="Undefined"
     rel="window">Undefined</a><input class="hiddenType" id="field.intro.setting"
     name="field.intro.setting" type="hidden" value="" rel="window"
     /><input class="hiddenType" id="field.intro.intid"
     name="field.intro.intid" type="hidden" value="" rel="window" />

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
