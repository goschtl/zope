=======================
Refererences to Objects
=======================


ViewReference
-------------

A view reference is used to store information about how to show the target of
a relation. The reference is an annotation for a data relation.

  >>> from z3c.reference.reference import viewReferenceFactory
  >>> from zope import component
  >>> component.provideAdapter(viewReferenceFactory)

  >>> from lovely.relation.dataproperty import DataRelationship
  >>> from z3c.reference.interfaces import IViewReference
  >>> rel = DataRelationship()
  >>> viewRef = IViewReference(rel)
  >>> viewRef
  <z3c.reference.reference.ViewReference object at ...>
  >>> viewRef.view = u'@resize?w=50&h=100'
  Traceback (most recent call last):
  ...
  WrongType: (u'@resize?w=50&h=100', <type 'str'>, 'view')
  >>> viewRef.view = '@resize?w=50&h=100'
  >>> viewRef.view
  '@resize?w=50&h=100'


ViewReferenceSettings
---------------------

Fields define a settingName, by default this name is a empty string if not
explicit given. This settingName is used for call a related named adapter
providing IViewReferenceSettings which provides a dictionary with
arbitrary information that is specific to the implementation
under the attribute ``settings``.

This settings are used for help to setup a reference editor. Let's see how
this works. By default, we get the DefaultViewReferenceSetting adapter for a
referenced object:

  >>> from zope import interface
  >>> from z3c.reference.interfaces import IViewReferenceSettings
  >>> from z3c.reference.reference import DefaultViewReferenceSettings
  >>> component.provideAdapter(DefaultViewReferenceSettings,
  ...                               (interface.Interface,))

  >>> class Content(object):
  ...     interface.implements(interface.Interface)
  ...     __name__ = None
  >>> content = Content()
  >>> adapter = IViewReferenceSettings(content)
  >>> adapter
  <DefaultViewReferenceSettings None>

The default adapter provides a empty dictionary:

  >>> adapter.settings
  {}

