##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Validation Exceptions

$Id: interfaces.py 30595 2005-06-01 22:14:18Z fdrake $
"""
__docformat__ = 'restructuredtext'

from zope.schema.interfaces import ValidationError
import zope.subview.interfaces
from zope.interface import Attribute, Interface, implements
from zope.schema import Bool

# TODO: dots in names

marker = object()

class ConversionError(ValueError):
    """ Value could not be converted to correct type """

class IWidget(zope.subview.interfaces.ISubview):
    """Generically describes the behavior of a widget.
    
    Note that all state calculation (e.g., gathering value from request) must
    happen within initialize.
    """

    label = Attribute(
        """The widget label.

        Label may be translated for the request.""")

    hint = Attribute(
        """A hint regarding the use of the widget.

        Hints are traditionally rendered using tooltips in GUIs, but may be
        rendered differently depending on the UI implementation.

        Hint may be translated for the request.""")

    required = Bool(
        title=u"Required",
        description=u"""If True, widget should be displayed as requiring input.

        By default, this value is the field's 'required' attribute. This
        field can be set to False for widgets that always provide input (e.g.
        a checkbox) to avoid unnecessary 'required' UI notations.
        """)
        
    error = Attribute(""" An exception created by initialize or setValue.  If 
        this value is not None, it is raised when getValue is called.
        
        Minimally, an exception object is expected to be adaptable to
        a view named snippet.""")
    
    message =  Attribute(""" A message object created in initialize or 
        setValue.  Minimally, a message object is expected to be adaptable to
        a view named snippet.
        """)
        
    def hasInput():
        """True if subview has a user-visible (client-side) state from a
        previous rendering (either persistently or from the most recent
        initialization).
        """
        
    def update(parent=None, name=None, value=marker):
        """ Initialize widget, calculating all state; and set its value.
        
        See ISubview.initialize for essential basic behavior.

        If the value is not provided, it will try to calculate the value from
        the environment (e.g., the a browser request).

        After a call to initialize, if the widget's value is not valid, its
        error attribute will contain either a ConversionError or
        zope.schema.interfaces.ValidationError.  If a widget wishes to add an
        object to message, that may be done here."""

    def getValue():
        """ Return the current value as set by initialize or setValue.

        Value is *not* validated.  Value should not be used to assign to 
        a field unless the widget's error attribute is None.
        
        May raise ConversionError (i.e., widget has state but does not
        know how to convert it to a validatable value) but not
        ValidationError.  For instance, if the widget's value is currently a
        required field's missing value, getValue must return the missing value.
        
        If setValue was called and did not raise an exception, the value
        must be returnable by this method."""
        
    def setValue(value):
        """ Sets the current value of the widget.  Resets the error and 
        message attributes to only the message and error pertaining 
        to the new value, if any.  Must minimally accept the widget's field's
        missing value and valid values.
        """
    
class IInputWidget(IWidget):
    """a widget used for input"""

class IDisplayWidget(IWidget):
    """a widget used for display"""

class IBrowserInputWidget(IWidget):
    """a browser widget used for input"""

class IBrowserDisplayWidget(IWidget):
    """a browser widget used for display"""

class ICoreWidget(interface.Interface):
    """A private interface to support lean widgets usable in both the old and
    new widget frameworks.
    
    The interface intends to allow for full flexibility by the widget author,
    while enforcing the patterns needed by the subview and widget interfaces.
    The only particularly unusual approach is using a state object to pass
    calculated values.  This state should not depend on the widget's name or
    prefix for use.  It encourages all state calculation to be done once,
    as is necessary for the initialize method.
    """

    def renderInvalidValue(context, request, name, value):
        """render a widget for an invalid value; typically renders a widget
        with an empty value.
        
        This is only called if calculateState returned None, or if
        a value has been explicitly set on the widget; and the value is
        invalid, according to the widget's field (context)."""

    def renderValidValue(context, request, name, value):
        """render a widget for the given valid value
        
        This is only called if calculateState returned None, or if
        a value has been explicitly set on the widget; and the value is
        valid, according to the widget's field (context)."""

    def renderState(context, request, name, state):
        """render a widget for the given valid (non-None) state.
        
        This is called if calculateState returned a non-None value and the
        widget's value was not set explicitly.
        """

    def calculateState(context, request, name):
        """return the widget's state object if the (logical) widget was
        rendered previously, or None.
        
        State must be persistable."""

    def calculateValue(state):
        """given a state provided by calculateState, return a value, or raise
        ConversionError"""

    def needsRedraw(context, request, state):
        """return a boolean on whether the given state (provided by
        calculateState) suggests that the widget should be redrawn (for
        instance, because the widget processed an internal submit)."""
