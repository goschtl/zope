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
"""Browser widgets with file-based input

$Id$
"""
__docformat__ = 'restructuredtext'


from zope.interface import implements

from zope.app.form.interfaces import IInputWidget, ConversionError
from zope.app.form.browser.widget import SimpleInputWidget, renderElement
from zope.app.form import InputWidget
from zope.app.form.browser.widget import BrowserWidget
from zope.app.form.browser.textwidgets import BytesWidget
from zope.app.form.browser.widget import DisplayWidget
from zope.app.form.browser.textwidgets import escape
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


# dependency
from zope.app.file.file import Mime

# used from ObjectWidget
from zope.schema import getFieldNamesInOrder
from zope.app.form.utility import setUpEditWidgets, applyWidgetsChanges




class MimeWidgetView:

    template = ViewPageTemplateFile('mimewidget.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def __call__(self):
        return self.template()


class MimeWidget(BrowserWidget, InputWidget):
    """MimeWidget renders the subwidgets for the interface IMime.
    
    The widget also extracts the filename and the fileupload to the session. 
    The subwidgets MimeDataWidget and MimeTypeWidget will access this 
    information for storing the fileupload and the mime-type.
    
    For more information about widgets which render subwidgets see the 
    ObjectWidget implementation in 
    'zope.app.form.browser.objectwidget.ObjectWidget'.
    """

    implements(IInputWidget)
    
    _object = None      # the object value (from setRenderedValue & request)
    _request_parsed = False

    def __init__(self, context, request, **kw):
        super(MimeWidget, self).__init__(context, request)
        
        # define view that renders the widget
        self.view = MimeWidgetView(self, request)

        # factory used to create content that this widget (field)
        # represents
        self.factory = Mime

        # handle foo_widget specs being passed in
        self.names = getFieldNamesInOrder(self.context.schema)
        for k, v in kw.items():
            if k.endswith('_widget'):
                setattr(self, k, v)

        # set up my subwidgets
        self._setUpEditWidgets()

    def setPrefix(self, prefix):
        super(ObjectWidget, self).setPrefix(prefix)
        self._setUpEditWidgets()

    def _setUpEditWidgets(self):
        # subwidgets need a new name
        setUpEditWidgets(self, self.context.schema, source=self.context,
                         prefix=self.name, names=self.names, 
                         context=self.context)

    def __call__(self):
        return self.view()
        
    def legendTitle(self):
        return self.context.title or self.context.__name__

    def getSubWidget(self, name):
        return getattr(self, '%s_widget' % name)
            
    def subwidgets(self):
        return [self.getSubWidget(name) for name in self.names]

    def hidden(self):
        """Render the list as hidden fields."""
        result = []
        for name in self.names:
            result.append(getSubwidget(name).hidden())
        return "".join(result)

    def getInputValue(self):
        """Return converted and validated widget data.

        The value for this field will be represented as an `ObjectStorage`
        instance which holds the subfield values as attributes. It will
        need to be converted by higher-level code into some more useful
        object (note that the default EditView calls `applyChanges`, which
        does this).
        """
        content = self.factory()
        for name in self.names:
            setattr(content, name, self.getSubWidget(name).getInputValue())
        return content

    def applyChanges(self, content):
        field = self.context

        # create our new object value
        value = field.query(content, None)
        if value is None:
            # TODO: ObjectCreatedEvent here would be nice
            value = self.factory()

        # apply sub changes, see if there *are* any changes
        # TODO: ObjectModifiedEvent here would be nice
        changes = applyWidgetsChanges(self, field.schema, target=value,
                                      names=self.names)

        # if there's changes, then store the new value on the content
        if changes:
            field.set(content, value)

        return changes

    def hasInput(self):
        """Is there input data for the field

        Return ``True`` if there is data and ``False`` otherwise.
        """
        for name in self.names:
            if self.getSubWidget(name).hasInput():
                return True
        return False

    def setRenderedValue(self, value):
        """Set the default data for the widget.

        The given value should be used even if the user has entered
        data.
        """
        # re-call setupwidgets with the content
        self._setUpEditWidgets()
        for name in self.names:
            self.getSubWidget(name).setRenderedValue(getattr(value, name, None))
            


class MimeDataWidget(SimpleInputWidget):
    """MimeDataWidget extracts the fileupload information from the session.
    
    The session is initiated from the MimeWidget and contains the fileupload.
    The method _toFieldValue() reads the fileupload (input) from the session.
    """
    type = 'file'

    default = ''
    displayWidth = 20
    displayMaxWidth = ""
    extra = ''
    style = ''
    convert_missing_value = True

    def __call__(self):
        # XXX set the width to 40 to be sure to recognize this widget
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=40,
                                 maxlength=40,
                                 extra=self.extra)
        else:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=40,
                                 extra=self.extra)

    def _toFieldValue(self, input):
        if input == '':
            return self.context.missing_value
        try:
            seek = input.seek
            read = input.read
        except AttributeError, e:
            raise ConversionError('Form input is not a file object', e)
        else:
            # if the FileUpload instance has no filename set, there is
            # no upload.
            if getattr(input, 'filename', ''):
                return input
            else:
                return self.context.missing_value

    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        # need to test for value, as an empty field is not an error, but
        # the current file should not be replaced.
        if value and (field.query(content, self) != value):
            field.set(content, value)
            return True
        else:
            return False


# TODO: add better description.

# till now we use a simply BytesWidget, later we can make use of a vocabulary
# for list the encoding via a Choice field 
class MimeDataEncodingWidget(BytesWidget):
    """MimeDataEncodingWidget set the encoding on text-based data.
    
    If we have a file with a mime-type 'text/...' we can set the encoding.
    """

# till now we use a simply BytesWidget, later we can make use of a vocabulary
# for list the encoding via a Choice field 
class MimeTypeWidget(BytesWidget):
    """MimeTypeWidget is used for to guess the mime-type.
    
    The session is initiated from the MimeWidget and contains the filename.
    The method _toFieldValue() reads the filename (input) from the session
    and finds the mime-type via the python mimetypes lib.
    """
    pass


class MimeDisplayWidget(DisplayWidget):
    """Mime data display widget."""
    # There need to be probably some widget options to determine how
    # the file is displayed, e.g. as a download link.

    def __call__(self):
        if self._renderedValueSet():
            content = self._data
        else:
            content = self.context.default

        show = u"Filename %s, size in bytes: %s" (content.filename,
                                                  content.getSize())
        return renderElement("span", contents=escape(show))



# TODO remove old implementations
class FileWidget(SimpleInputWidget):
    """File Widget"""

    type = 'file'

    default = ''
    displayWidth = 20
    displayMaxWidth = ""
    extra = ''
    style = ''
    convert_missing_value = True

    def __call__(self):
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=self.displayWidth,
                                 maxlength=displayMaxWidth,
                                 extra=self.extra)
        else:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=self.displayWidth,
                                 extra=self.extra)

    def _toFieldValue(self, input):
        if input == '':
            return self.context.missing_value
        try:
            seek = input.seek
            read = input.read
        except AttributeError, e:
            raise ConversionError('Form input is not a file object', e)
        else:
            seek(0)
            data = read()
            if data or getattr(input, 'filename', ''):
                return data
            else:
                return self.context.missing_value

# TODO: remove it
class XXXMimeWidget(SimpleInputWidget):
    u"""Mime file upload widget"""

    type = 'file'

    default = ''
    displayWidth = 20
    displayMaxWidth = ""
    extra = ''
    style = ''
    convert_missing_value = True

    def __call__(self):
        # XXX set the width to 40 to be sure to recognize this widget
        displayMaxWidth = self.displayMaxWidth or 0
        if displayMaxWidth > 0:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=40,
                                 maxlength=40,
                                 extra=self.extra)
        else:
            return renderElement(self.tag,
                                 type=self.type,
                                 name=self.name,
                                 id=self.name,
                                 cssClass=self.cssClass,
                                 size=40,
                                 extra=self.extra)

    def _toFieldValue(self, input):
        if input == '':
            return self.context.missing_value
        try:
            seek = input.seek
            read = input.read
        except AttributeError, e:
            raise ConversionError('Form input is not a file object', e)
        else:
            # if the FileUpload instance has no filename set, there is
            # no upload.
            if getattr(input, 'filename', ''):
                return input
            else:
                return self.context.missing_value

    def applyChanges(self, content):
        field = self.context
        value = self.getInputValue()
        # need to test for value, as an empty field is not an error, but
        # the current file should not be replaced.
        if value and (field.query(content, self) != value):
            field.set(content, value)
            return True
        else:
            return False
