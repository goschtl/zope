##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""File content component

$Id:$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from transaction import get_transaction
from zope.interface import implements

from zope.schema.interfaces import IBytes
from zope.schema._bootstrapfields import Field
from zope.schema._bootstrapfields import TextLine
from zope.schema._field import Bytes
from zope.app.file.file import File

# import for the FileDataWidget
from zope.app.form.browser import FileWidget
from zope.app.form.browser.widget import renderElement

from zope.i18nmessageid import MessageIDFactory
_ = MessageIDFactory("zope")

from interfaces import IFile

#
# The basic schema interface
#
class IMime(IBytes):
    u"""Fields which hold data characterized by a mime type.

    The data is stored memory effecient.
    """

    contentType = TextLine(title=_(u"Mime type"),
                        description=_(u"The mime type of the stored data"),
                        required=False,
                        default=u"application/octet-stream"
                        )

    def getSize():
        u"""Return the size of the stored data in bytes."""

class IFileData(IMime):
    u"""Fields which hold uploaded data, mainly file type data"""
    
    filename = TextLine(title=_(u"Filename"),
                        description=_(u"The Filename of the uploaded file"),
                        required=False)
    
# The field implementation, does currently assume to handle file-like data
class FileData(Bytes):
    u"""A field implementation for uploaded files. """

    implements(IFileData)

    def set(self, obj, value):
        """
        Do a two phase save, first create an empty file object, make it persistent
        than read the data into it in chunks, to reduce memory consumption.

        'value' is a FileUpload object.
        """
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               obj.__class__.__module__,
                               obj.__class__.__name__))
        # now create an empty file object and store it at the persistent object
        setattr(obj, self.__name__, FileDataValue())
        file = getattr(obj, self.__name__)
        # now do the upload in chunks
        file.data = value 
        filename = self._extractFilename(value)
        file.filename = filename

    def _validate(self, value):
        # just test for the seek method of FileUpload instances.
        if value and not getattr(value, 'seek',''):
            raise WrongType(value, self._type)

    def _extractContentType(self, data):
        u"""Extract the content type for the given data"""
        # XXX Need to call some function here
        return 'application/octet-stream'
    
    def _extractFilename(self, data):
        # if it is a fileupload object
        if hasattr(data,'filename'):
            fid = data.filename
            # some browsers include the full pathname
            fid=fid[max(fid.rfind('/'),
                        fid.rfind('\\'),
                        fid.rfind(':')
                              )+1:]
            return fid
        else:
            return ''

class FileDataWidget(FileWidget):
    u"""a simple file upload widget"""

    type = 'file'

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

class FileDataValue(File):
    u"""Inherit a normal file content object."""

    def __init__(self, *args):
        super(File, self).__init__(*args)
        self.filename = ''

