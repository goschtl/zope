"""
Test the adapter factory.

  >>> import grok
  >>> import zope.component
  >>> grok.grok('mars.adapter.tests.adapter')

  >>> from mars.adapter.tests.adapter import Field, IValue
  >>> field = Field()

  >>> print zope.component.queryAdapter(field, IValue, name='named')
  NamedValue

  >>> print zope.component.queryAdapter(field, IValue)
  UnNamedValue


"""
import zope.interface
import zope.component

import grok
import mars.adapter

class IValue(zope.interface.Interface):
    """A value."""

class IField(zope.interface.Interface):
    """A field"""

class Field(grok.Model):
    """A field"""
    zope.interface.implements(IField)

class UnNamedValue(object):
    """Static value adapter."""
    zope.component.adapts(IField)
    zope.interface.implements(IValue)

    def __init__(self, context):
        self.context = context

    def __repr__(self):
        return self.__class__.__name__

class UnNamedValueAdapter(mars.adapter.AdapterFactory):
    mars.adapter.factory(UnNamedValue)

class NamedValue(object):
    """Static value adapter."""
    zope.component.adapts(IField)
    zope.interface.implements(IValue)

    def __init__(self, context):
        self.context = context

    def __repr__(self):
        return self.__class__.__name__

class NamedValueAdapter(mars.adapter.AdapterFactory):
    grok.name('named')
    mars.adapter.factory(NamedValue)

