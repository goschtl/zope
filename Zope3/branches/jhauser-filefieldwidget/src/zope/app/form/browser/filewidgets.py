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
from zope.app.form.browser.textwidgets import BytesWidget
from zope.app.form.browser.widget import DisplayWidget
from zope.app.form.browser.textwidgets import escape


class MimeWidget(SimpleInputWidget):
    """MimeWidget renders the subwidgets for the interface IMime.
    
    The widget also extracts the filename and the fileupload to the session. 
    The subwidgets MimeDataWidget and MimeTypeWidget will access this 
    information for storing the fileupload and the mime-type.
    
    For more information about widgets which render subwidgets see the 
    ObjectWidget implementation in 
    'zope.app.form.browser.objectwidget.ObjectWidget'.
    """
    pass


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
