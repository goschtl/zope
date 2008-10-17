===================
z3c.relationfieldui 
===================

This package implements a widget for relations as defined by
`z3c.relationfield`_.

.. `_z3c.relationfield`: http://pypy.python.org/pypi/z3c.relationfield

Setup
-----

In order to demonstrate our widget, we need to set up a relation field.

We first need to grok ftests to make sure we have the right utilities
registered::

  >>> import grok
  >>> grok.testing.grok('z3c.relationfieldui.ftests')

Let's set up a test application with content in it, including a relation
from ``b`` to ``a``::

  >>> root = getRootFolder()['root'] = TestApp()
  >>> from zope.app.component.hooks import setSite
  >>> setSite(root)
  >>> root['a'] = Item()
  >>> from z3c.relationfield import RelationValue
  >>> b = Item()
  >>> from zope import component
  >>> from zope.app.intid.interfaces import IIntIds
  >>> intids = component.getUtility(IIntIds)
  >>> a_id = intids.getId(root['a'])
  >>> b.rel = RelationValue(a_id)
  >>> root['b'] = b

We also need to set up a utility that knows how to generate an object
path for a given object, and back::

  >>> from z3c.objpath.interfaces import IObjectPath
  >>> class ObjectPath(grok.GlobalUtility):
  ...   grok.provides(IObjectPath)
  ...   def path(self, obj):
  ...       return obj.__name__
  ...   def resolve(self, path):
  ...       return root[path]

  >>> grok.testing.grok_component('ObjectPath', ObjectPath)
  True

The relation widget
-------------------

The relation widget can be looked up for a relation field. The widget
will render with a button that can be used to set the
relation. Pressing this button will show a pop up window. The URL
implementing the popup window is defined on a special view that needs
to be available on the context object (that the relation is defined
on). This view must be named "explorerurl". We'll provide one here::

  >>> from zope.interface import Interface
  >>> class ExplorerUrl(grok.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      return 'http://grok.zope.org'

XXX in order to grok a view in the tests we need to supply the
``BuiltinModuleInfo`` class with a ``package_dotted_name`` attribute.
This should be fixed in Martian::

  >>> from martian.scan import BuiltinModuleInfo
  >>> BuiltinModuleInfo.package_dotted_name = 'foo'

Now we can Grok the view::

  >>> grok.testing.grok_component('ExplorerUrl', ExplorerUrl)
  True

Let's take a look at the relation widget now::

  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.relationfieldui import RelationWidget
  >>> request = TestRequest()
  >>> widget = RelationWidget(IItem['rel'], request)
  >>> print widget()
  <input class="textType" id="field.rel" name="field.rel" size="20" type="text" value=""  /><input class="buttonType" onclick="Z3C.relation.popup(this.previousSibling, 'http://grok.zope.org')" type="button" value="get relation" />

Relation display widget
-----------------------

The display widget for relation will render a URL to the object it relates
to. What this URL will be exactly can be controlled by defining a view
on the object called "relationurl". Without such a view, the display
widget will link directly to the object::

  >>> from z3c.relationfieldui import RelationDisplayWidget
  >>> widget = RelationDisplayWidget(IItem['rel'], request)

We have to set the widget up with some data::

  >>> widget._data = b.rel 

The widget will point to the plain URL of ``rel``'s ``to_object``::

  >>> print widget()
  <a href="http://127.0.0.1/root/a">a</a>

Now we register a special ``relationurl`` view::

  >>> class RelationUrl(grok.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      return self.url('edit')
  >>> grok.testing.grok_component('RelationUrl', RelationUrl)
  True

We should now see a link postfixed with ``/edit``::

  >>> print widget()
  <a href="http://127.0.0.1/root/a/edit">a</a>
