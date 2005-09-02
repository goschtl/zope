from zope import interface, component
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.widget import interfaces
import zope.app.form.interfaces # import IWidget, InputErrors
from zope.schema.interfaces import ValidationError

class LegacyValidationError(ValidationError):
    """a validation error that wraps an old style
    zope.app.form.interfaces.WidgetInputError"""
    def __init__(self, error):
        self.error = error

class LegacyConversionError(interfaces.ConversionError):
    def __init__(self, error):
        self.error = error

class LegacyInputWidgetAdapter(object):
    def __init__(self, widget):
        self._widget = widget
        context = widget.context
        self.context = context
        self.request = widget.request
        self.label = context.title
        self.hint = context.description
        self.required = context.required

    name = property(lambda self: self._widget.name)

    _prefix = None
    def prefix(self, value):
        self._prefix = value # no API to get from legacy interface
        self._widget.setPrefix(value)
    prefix = property(lambda self: self._prefix, prefix)

    _error = None
    error = property(lambda self: self._error)
    
    message = property(lambda self: None)

    def getState(self):
        raise NotImplementedError(
            'Legacy Widget Adapter does not implement getState')

    def hasState(self):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        return self._widget.hasInput()

    def setValue(self, value):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        self._value = value
        self._widget.setRenderedValue(value)
        self._error = None
    
    _value = None
    def getValue(self):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        if self.error is not None:
            raise self.error
        return self._value

    def initialize(self, prefix=None, value=interfaces.marker, state=None):
        if state is not None:
            raise NotImplementedError(
                'Legacy Widget Adapter does not implement initializing from '
                'state')
        self._initialized = True
        self.prefix = prefix
        if value is interfaces.marker:
            try:
                self._value = self._widget.getInputValue()
            # let ValidationErrors pass through
            except ValidationError, e:
                self._error = e
            except zope.app.form.interfaces.WidgetInputError, e:
                self._error = LegacyValidationError(e)
            except zope.app.form.interfaces.ConversionError, e:
                self._error = LegacyConversionError(e)
        else:
            self.setValue(value)
