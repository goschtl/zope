##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: interfaces.py,v 1.3 2004/04/24 23:19:42 srichter Exp $
"""
from zope.interface import Interface
from zope.app.form.interfaces import IWidget

class IAddFormCustomization(Interface):
    """This interface defined methods of add forms that can be overridden

    Classes supplied when defining add forms may need to override some
    of these methods.

    In particular, when the context of an add form is not an IAdding,
    a subclass needs to override ``nextURL`` and one of ``add`` or
    ``createAndAdd``.

    To see how all this fits together, here's pseudo code for the
    update() method of the form:

    def update(self):
        data = <get data from widgets> # a dict
        self.createAndAdd(data)
        self.request.response.redirect(self.nextURL())

    def createAndAdd(self, data):
        content = <create the content from the data>
        content = self.add(content) # content wrapped in some context
        <set after-add attributes on content>

    """

    def createAndAdd(data):
        """Create a new object from the given data and the resulting object.

        The data argument is a dictionary with values supplied by the form.

        If any user errors occur, they should be collected into a list
        and raised as a WidgetsError.

        (For the default implementation, see pseudo-code in class docs.)
        """

    def add(content):
        """Add the given content

        This method is overridden when the context of the add form is
        not an IAdding.  In this case, the class that customizes the
        form must take over adding the object.

        The content should be returned wrapped in the context of the
        object that it was added to.

        The default implementation returns self.context.add(content),
        i.e. it delegates to the IAdding view.
        """

    def nextURL():
        """Return the URL to be displayed after the add operation.

        This can be relative to the view's context.

        The default implementation returns self.context.nextURL(),
        i.e. it delegates to the IAdding view.
        """


class IBrowserWidget(IWidget):
    """A field widget contains all the properties that are required
       to represent a field. Properties include css_sheet,
       default value and so on.
    """

    def __call__(): # XXX promote to IWidget?
        """Render the widget
        """

    def hidden():
        """Render the widget as a hidden field
        """

    def label():
        """Render a label tag"""

    def error(): # XXX promote to IWidget?
        """Render the validation error for the widget, or return
        an empty string if no error"""

    def row():
        """Render the widget as two or three div elements,
           for the label, the field and possibly the validation error

        For example:
          <div class="label">label</div><div class="field">field</div>
          <div class="error">Validation error message</div>
        """


class IFormCollaborationView(Interface):
    """Views that collaborate to create a single form

    When a form is applied, the changes in the form need to
    be applied to individual views, which update objects as
    necessary.
    """

    def __call__():
        """Render the view as a part of a larger form.

        Form input elements should be included, prefixed with the
        prefix given to setPrefix.

        'form' and 'submit' elements should not be included. They
        will be provided for the larger form.
        """

    def setPrefix(prefix):
        """Set the prefix used for names of input elements

        Element names should begin with the given prefix,
        followed by a dot.
        """

    def update():
        """Update the form with data from the request.
        """


class IVocabularyQueryView(Interface):
    """View support for IVocabularyQuery objects.

    Implementations of this interface are used by vocabulary field
    edit widgets to support query and result presentations.
    """

    def __init__(query, field, request):
        """This is a multiview, which is looked up for (query, field) pairs."""

    def setName(name):
        """Set the name used to compute the form field names.

        Form field names should be the given name, or additional name
        components separated by dots may be appended if multiple form
        fields are needed.

        This method will be called after the IVocabularyQueryView has
        been created and before performAction() is called.
        """


    def setWidget(widget):
        """Set the widget using this query view.

        This allows the query view to take advantage of rendering
        helper methods made available by the widget.

        This method will be called after the IVocabularyQueryView has
        been created and before performAction() is called.
        """

    def performAction(value):
        """Perform any action indicated by any submit buttons in the
        sub-widget.

        'value' is the current value of the field.  Submit actions may
        cause the value to be modified.  If so, the new value should
        be returned; otherwise the old value should be returned.

        Actions should only be performed if a submit button provided
        by the view was selected.

        This method will be called after setName() and setWidget() and
        before renderInput() or renderResults().
        """

    def renderInput():
        """Return a rendering of the input portion of the widget."""

    def renderResults(value):
        """Return a rendering of the results portion of the widget.

        'value' is the current value represented by the widget.
        """

class IWidgetInputErrorView(Interface):
    """Display an input error as a snippet of text."""

    def snippet():
        """Convert a widget input error to an html snippet."""
