*******************
z3c.relationfieldui 
*******************

This package implements a ``zope.formlib`` compatible widget for
relations as defined by `z3c.relationfield`_.

.. _`z3c.relationfield`: http://pypi.python.org/pypi/z3c.relationfield

This package does not provide a ``z3c.form`` widget for
``z3c.relationfield``, but it is hoped that will eventually be
developed as well (in another package).

Setup
=====

In order to demonstrate our widget, we need to first set up a relation
field (for the details of this see z3c.relationfield's
documentation)::

  >>> from z3c.relationfield import Relation
  >>> from zope.interface import Interface
  >>> class IItem(Interface):
  ...   rel = Relation(title=u"Relation")
  >>> from z3c.relationfield.interfaces import IHasRelations
  >>> from persistent import Persistent
  >>> from zope.interface import implements
  >>> class Item(Persistent):
  ...   implements(IItem, IHasRelations)
  ...   def __init__(self):
  ...     self.rel = None
  >>> from zope.app.component.site import SiteManagerContainer
  >>> from zope.app.container.btree import BTreeContainer
  >>> class TestApp(SiteManagerContainer, BTreeContainer):
  ...   pass

Set up the application with the right utilities::

  >>> root = getRootFolder()['root'] = TestApp()
  >>> from zope.app.component.site import LocalSiteManager
  >>> root.setSiteManager(LocalSiteManager(root))
  >>> from zope.app.component.hooks import setSite
  >>> setSite(root)
  >>> from zope.app.intid import IntIds
  >>> from zope.app.intid.interfaces import IIntIds
  >>> root['intids'] = intids = IntIds() 
  >>> sm = root.getSiteManager()
  >>> sm.registerUtility(intids, provided=IIntIds)
  >>> from z3c.relationfield import RelationCatalog
  >>> from zc.relation.interfaces import ICatalog
  >>> root['catalog'] = catalog = RelationCatalog()
  >>> sm.registerUtility(catalog, provided=ICatalog)

Items ``a`` and ``b`` with a relation from ``b`` to ``a``::

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

  >>> import grokcore.component as grok
  >>> from z3c.objpath.interfaces import IObjectPath
  >>> class ObjectPath(grok.GlobalUtility):
  ...   grok.provides(IObjectPath)
  ...   def path(self, obj):
  ...       return obj.__name__
  ...   def resolve(self, path):
  ...       try:
  ...           return root[path]
  ...       except KeyError:
  ...           raise ValueError("Cannot resolve: %s" % path)
  >>> grok.testing.grok_component('ObjectPath', ObjectPath)
  True

Let's also set up a broken relation::

  >>> d = root['d'] = Item()
  >>> d_id = intids.getId(root['d'])
  >>> c = Item()
  >>> c.rel = RelationValue(d_id)
  >>> root['c'] = c
  >>> del root['d']
  >>> root['c'].rel.to_object is None
  True
  >>> root['c'].rel.isBroken()
  True

The relation widget
===================

The relation widget can be looked up for a relation field. The widget
will render with a button that can be used to set the
relation. Pressing this button will show a pop up window. The URL
implementing the popup window is defined on a special view that needs
to be available on the context object (that the relation is defined
on). This view must be named "explorerurl". We'll provide one here::

  >>> from zope.interface import Interface
  >>> import grokcore.view
  >>> class ExplorerUrl(grokcore.view.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      return 'http://grok.zope.org'

Now we can Grok the view::

  >>> grok.testing.grok_component('ExplorerUrl', ExplorerUrl)
  True

Let's take a look at the relation widget now::

  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.relationfieldui import RelationWidget
  >>> request = TestRequest()
  >>> field = IItem['rel']
  >>> bound = field.bind(root['b'])
  >>> widget = RelationWidget(bound, request)
  >>> widget.setRenderedValue(bound.get(root['b']))
  >>> print widget()
  <input class="textType" id="field.rel" name="field.rel" size="20" type="text" value="a"  /><input class="buttonType" onclick="Z3C.relation.popup(this.previousSibling, 'http://grok.zope.org?from_attribute=rel&amp;from_path=b')" type="button" value="get relation" />

Let's also try it with the broken relation::

  >>> bound = field.bind(root['c'])
  >>> widget = RelationWidget(bound, request)
  >>> widget.setRenderedValue(bound.get(root['c']))

When we render the widget, the value is still correct (even though
it's broken)::

  >>> print widget()
  <input class="textType" id="field.rel" name="field.rel" size="20" type="text" value="d"  /><input class="buttonType" onclick="Z3C.relation.popup(this.previousSibling, 'http://grok.zope.org?from_attribute=rel&amp;from_path=c')" type="button" value="get relation" />

Relation display widget
=======================

The display widget for relation will render a URL to the object it relates
to. What this URL will be exactly can be controlled by defining a view
on the object called "relationurl". Without such a view, the display
widget will link directly to the object::

  >>> from z3c.relationfieldui import RelationDisplayWidget
  >>> bound = field.bind(root['b'])
  >>> widget = RelationDisplayWidget(bound, request)
  >>> widget.setRenderedValue(bound.get(root['b']))

The widget will point to the plain URL of ``rel``'s ``to_object``::

  >>> print widget()
  <a href="http://127.0.0.1/root/a">a</a>

Now we register a special ``relationurl`` view::

  >>> class RelationUrl(grokcore.view.View):
  ...   grok.context(Interface)
  ...   def render(self):
  ...      return self.url('edit')
  >>> grok.testing.grok_component('RelationUrl', RelationUrl)
  True

We should now see a link postfixed with ``/edit``::

  >>> print widget()
  <a href="http://127.0.0.1/root/a/edit">a</a>

When the relation is broken, it will still display, but as broken::

  >>> bound = field.bind(root['c'])
  >>> widget = RelationDisplayWidget(bound, request)
  >>> widget.setRenderedValue(bound.get(root['c']))
  >>> print widget()
  Broken relation to: d
