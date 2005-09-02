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
from zope.component.interfaces import IView
from zope.interface import Attribute, Interface, implements
from zope.schema import Bool

# TODO: dots in names

class ConversionError(ValueError):
    """ Value could not be converted to correct type """
    
class InvalidStateError(RuntimeError):
    """ This widget's state has been invalidated by a call to setValue()"""

class IBaseWidget(IView):
    """Generically describes the behavior of a widget.

    Note that this level must be still presentation independent.
    """

    name = Attribute(
        """The unique widget name

        This must be unique within a set of widgets.""")

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
    
class IWidget(IBaseWidget):
    """ new interface for widget """
    
    def __call__():
        """ render widget """
        
    def initialize(prefix=None, value=None, state=None):
        """ Initialize widget and set its value.

        Initialize must be called before any other method besides __init__.

        If prefix is passed in, the prefix attribute of the widget is set.
        Prefix must be None or be a string.  See prefix attribute for more 
        detail.
        
        If neither value nor state is included, the widget will try
        to set its value from the request.  

        If value is passed in, the widget will use that value.  If state is 
        passed in, the widget will use the state object to set its value and
        do any other initialization desired. The state object must be obtained 
        from the getState method of a widget of the same class.  
        
        Only one of value or state may be passed, passing both raises
        TypeError.        
        
        If the widget's value is not valid, its error attribute will contain 
        either a ConversionError or zope.schema.interfaces.ValidationError.  If 
        a widget wishes to add an object to message, that may be done here.
        """        
        
    def getState():
        """ If the widget has been viewed previously, returns a non-None, 
        picklable object representing the widget's state, unless setValue has 
        been called, in which case it raises InvalidStateError.  Otherwise, 
        returns None.

        A state object can later be passed in to initialize to restore the
        state of the widget.
        """
        
    def hasState():
        """ Return True if the widget has a state from a previous request.
        
        Should be equivalent to self.getState() is not None.
        """

    def getValue():
        """ Return the current value as set by initialize or setValue.

        If error is not None, raise it."""
        
    def setValue(value):
        """ Sets the current value of the widget.  Resets the error and 
        message attributes to only the message and error pertaining 
        to the new value, if any.
        """
                
    prefix = Attribute("""Element names should begin with the given `prefix`.
        Prefix name may be None, or a string.  Any other value raises 
        ValueError.  When prefixes are concatenated with the widget name, a dot 
        is used as a delimiter; a trailing dot is neither required nor suggested
        in the prefix itself. """)
        
    error = Attribute(""" An exception created by initialize or setValue.  If 
        this value is not None, it is raised when getValue is called.
        
        Minimally, an exception object is expected to be adaptable to
        a view named snippet.""")
    
    message =  Attribute(""" A message object created in initialize or 
        setValue.  Minimally, a message object is expected to be adaptable to
        a view named snippet.
        """)
    
class IInputWidget(IWidget):
    """a widget used for input"""

class IDisplayWidget(IWidget):
    """a widget used for display"""

