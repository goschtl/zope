# simple implementation of new widget API

from zope import interface
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema.interfaces import ValidationError
from xml.sax.saxutils import quoteattr

import zope.widget.interfaces

class BaseInputWidget(object):
    """base simple widget"""
    
    interface.implements(zope.widget.interfaces.IInputWidget)
    __doc__ = zope.widget.interfaces.IInputWidget.__doc__
    
    _name = None
    name = property(lambda self: self._name)

    _prefix = None
    def prefix(self, value):
        self._prefix = value
        if value is None:
            self._name = self.context.__name__
        else:
            self._name = '.'.join((value, self.context.__name__))
    prefix = property(lambda self: self._prefix, prefix)
    
    _error = None
    error = property(lambda self: self._error)

    _message = None
    message = property(lambda self: self._message)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.label = context.title
        self.hint = context.description
        self.required = context.required
        
    _valueForced = False
    _initialized = False    
    _state = None
    def initialize(self, prefix=None, value=None, state=None):
        self._initialized = True
        self.prefix = prefix
        if state is None:
            state = self._calculateStateFromRequest()
        else:
            if value is not None:
                raise TypeError('May pass only one of value and state')
        self._state = state
        if value is None:
            if self._state is None:
                value = self.context.default
            else:
                value = self._calculateValueFromState()
            self.setValue(value)
            self._valueForced = False
        else:
            self.setValue(value)
            
    def getState(self):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        if self._state is not None and self._valueForced:
            raise zope.widget.interfaces.InvalidStateError()
        return self._state
    
    def hasState(self):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        return self._state is not None
    
    _value = None
    def getValue(self):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        if self.error is not None:
            raise self.error
        return self._value
    
    def setValue(self, value):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        try:
            self.context.validate(value)
        except ValidationError, e:
            self._error = e
        else:
            self._error = None
        self._message = None
        self._value = value
        self._valueForced = True

    def __call__(self):
        raise NotImplementedError
        
    def _calculateStateFromRequest(self):
        """return the widget's state object if it was rendered previously, or
        None"""
        return self.request.form.get(self.name)

    def _calculateValueFromState(self):
        """return the current value on the basis of the _state attribute"""
        raise NotImplementedError
    

class AdvancedBaseInputWidget(BaseInputWidget):
    """base advanced widget"""

    def _calculateStateFromRequest(self):
        res = {}
        name = self.name
        len_name = len(name)
        prename = name + "."
        for n, v in self.request.form.items():
            if n == name or n.startswith(prename):
                res[n[len_name:]] = v
        return res or None

class TextLineWidget(BaseInputWidget):
    
    #template = namedtemplate.NamedTemplate('default')   
    
    t = ("""<input type="text" value=%(value)s name=%(name)s """
         """id=%(name)s size="20" />""")
    

    def __call__(self):
        if self._valueForced:
            value = self.getValue()
        else:
            value = self._state
        return self.t % {'value':quoteattr(value or ''),
                         'name':quoteattr(self.name)}

    #("""<input type="text" value=%(value)s name=%(name)s """
    #            """id=%(name)s size="20" />""")
    
    def _calculateValueFromState(self):
        try:
            value = unicode(self._state)
        except ValueError, v: # XXX
            e = zope.widget.interfaces.ConversionError(v)
        else:
            return value