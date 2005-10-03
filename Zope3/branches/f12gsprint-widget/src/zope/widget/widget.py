##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id: form.py 38007 2005-08-19 17:50:28Z poster $
"""
import persistent
import persistent.dict
from zope import interface
import zope.subview
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.schema.interfaces import ValidationError, RequiredMissing
from xml.sax.saxutils import quoteattr

from zope.widget import interfaces

class Widget(zope.subview.SubviewBase):
    """widget, designed to be used by composition or subclass to get core
    behavior"""
    
    interface.implements(interfaces.IWidget)
    __doc__ = interfaces.IInputWidget.__doc__
    
    _error = None
    error = property(lambda self: self._error)

    _message = None
    message = property(lambda self: self._message)
    
    def __init__(self, context, request, core_widget=None):
        self.context = context
        self.request = request
        self.label = context.title
        self.hint = context.description
        self.required = context.required
        assert core_widget is None or interfaces.ICoreWidget.providedBy(
            core_widget)
        self._core_widget = core_widget

    _valueForced = False
    def update(self, parent=None, name=None, value=interfaces.marker):
        super(Widget, self).initialize(parent, name)
        self._state = self._calculateState()
        if value is interfaces.marker:
            if not self.hasInput():
                self.setValue(self.context.default) # effectively a force
            else:
                try:
                    value = self._calculateValue()
                except interfaces.ConversionError, e:
                    self._error = e
                    self._message = None
                    self._value = self.context.missing_value
                else:
                    self.setValue(value)
                self._valueForced = False # not a force
        else:
            self.setValue(value) # this is a force.
    
    def hasInput(self):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        return self._state is not None
    
    _value = None
    def getValue(self):
        if not self._initialized:
            raise RuntimeError('Initialize widget first')
        if self.error is not None and isinstance(
            self.error, interfaces.ConversionError):
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

    # the following methods may typically either be overridden or be used
    # as is, delegating to an ICoreWidget implementation.

    def needsRedraw(self):
        return self._valueForced or (
            self._state is not None and self._core_widget.needsRedraw(
                self.context, self.request, self._state))
    needsRedraw = property(needsRedraw)

    def render(self):
        """render the widget.
        
        if self._valueForced:
            if self.error is not None:
                draw the widget with no value filled in
            else:
                draw the widget on the basis of the current value
        else:
            draw the widget on the basis of the _state (which should
            always be non-None if _valueForced is False)"""
        if self._valueForced:
            if self.error is not None:
                return self._core_widget.renderInvalidValue(
                    self.context, self.request, self.prefix, self._value)
            else:
                return self._core_widget.renderValidValue(
                    self.context, self.request, self.prefix, self._value)
        else:
            return self._core_widget.renderState(
                    self.context, self.request, self.prefix, self._state)
        
    def _calculateState(self):
        """return the widget's state object if the (logical) widget was
        rendered previously, or None."""
        return self._core_widget.calculateState(
            self.context, self.request, self.name)

    def _calculateValue(self):
        """return the current value only on the basis of the _state attribute.

        Do not validate.  If cannot generate a value from the current _state,
        raise zope.widget.interfaces.ConversionError.

        _state will never be None when this method is called."""
        return self._core_widget.calculateValue(self._state)

class CoreWidget(persistent.Persistent):

    interface.implements(interfaces.ICoreWidget)

    def renderInvalidValue(self, context, request, name, value):
        """render a widget for an invalid value"""
        raise NotImplementedError

    def renderValidValue(self, context, request, name, value):
        """render a widget for the given valid value"""
        raise NotImplementedError

    def renderState(self, context, request, name, state):
        """render a widget for the given state"""
        raise NotImplementedError

    def calculateState(self, context, request, name):
        """return the widget's state object if the (logical) widget was
        rendered previously, or None.
        
        This simple implementation is good for widgets that have only one
        input field."""
        return request.form.get(name+".value")

    def calculateValue(self, state):
        """given a state, return a value, or raise ConversionError"""
        raise NotImplementedError

    def needsRedraw(self, context, request, state):
        return False

class AdvancedCoreWidget(object):
    """base advanced widget"""

    def calculateState(self, context, request, name):
        """return the widget's state object if the (logical) widget was
        rendered previously, or None.
        
        This advanced implementation is good for widgets that are comprised
        of multiple input fields.  It means that the state object (if not None)
        is a dictionary."""
        res = persistent.dict.PersistentDict()
        prefix = self.prefix + "."
        slice = len(prefix)
        for n, v in request.form.items():
            if n.startswith(prefix):
                res[n[slice:]] = v
        return res or None

class CoreTextLineWidget(SimpleCoreWidget):

    def __init__(self, size='20', extra=''):
        self.size = size
        self.extra = extra

    def renderInvalidValue(self, context, request, name, value):
        return self.renderValidValue(name, '')

    def renderValidValue(self, context, request, name, value):
        return (
            """<input type="text" value=%(value)s name=%(name)s """
            """id=%(name)s size="%(size)s" %(extra)s />""" % 
            {'value': value, 'name': name+".value", 'size': self.size, 
             'extra': self.extra})
    renderState = renderValidValue

    def calculateValue(self, state):
        try:
            return unicode(state)
        except ValueError, v:
            raise interfaces.ConversionError(v)

textLineWidget = CoreTextLineWidget()

def TextLineWidget(context, request):
    w = InputWidget(context, request, textLineWidget)
    interface.directlyProvides(w, interfaces.IBrowserInputWidget)
    return w
