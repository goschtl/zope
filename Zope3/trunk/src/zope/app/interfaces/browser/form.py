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
$Id: form.py,v 1.8 2003/05/01 19:35:21 faassen Exp $
"""
from zope.interface import Interface
from zope.app.interfaces.form import IWidget

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

    def setPrefix(self, prefix):
        """Set the form-variable name prefix used for the widget

        The widget will define its own form variable names by
        concatinating the prefix and the field name using a dot. For
        example, with a prefix of "page" and a field name of "title",
        a form name of "page.title" will be used. A widget may use
        multiple form fields. If so, it should add distinguishing
        suffixes to the prefix and field name.
        """

    def __call__():
        """Render the widget
        """

    def hidden():
        """Render the widget as a hidden field
        """

    def label():
        """Render a label tag"""

    def row():
        """Render the widget as two div elements, for the label and the field.

        For example:
          <div class="label">label</div><div class="field">field</div>
        """

    # XXX The following two methods are being supported for backward
    # compatability. They are deprecated and will be refactored away
    # eventually.

    def render(value):
        """Renders this widget as HTML using property values in field.

        The value if given will be used as the default value for the widget.
        """

    def renderHidden(value):
        """Renders this widget as a hidden field.
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
