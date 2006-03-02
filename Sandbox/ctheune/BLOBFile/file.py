##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""BLOBFile object

$Id$
"""

import mimetypes
from Globals import DTMLFile
from webdav.common import rfc1123_date
from webdav.Lockable import ResourceLockedError
from webdav.WriteLockInterface import WriteLockInterface
from OFS.SimpleItem import SimpleItem
from ZPublisher.HTTPRequest import FileUpload
from zExceptions import Redirect
from ZODB.Blobs.Blob import Blob

from OFS.Image import Pdata

# Sibling imports
from ZPublisher.Iterators import filestream_iterator

manage_addFileForm = DTMLFile('dtml/fileAdd', globals(), Kind='File', 
        kind='file')

def manage_addFile(self, id, file='', title='', precondition='', 
        content_type='', REQUEST=None):
    """Add a new BLOBFile object.

    Creates a new file object 'id' with the contents of 'file'"""

    id = str(id)
    title = str(title)
    content_type = str(content_type)
    precondition = str(precondition)

    id, title = cookId(id, title, file)

    self = self.this()

    # First, we create the file without data:
    self._setObject(id, BLOBFile(id, title, '', content_type, precondition))

    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    if file:
        self._getOb(id).manage_upload(file)
    if content_type:
        self._getOb(id).content_type=content_type

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')

class BLOBFile(SimpleItem):
    """A BLOBFile object is a content object for large binary files."""

    __implements__ = (WriteLockInterface,)
    meta_type = 'BLOBFile'

    precondition = ''
    size = None
    alt = ''

    manage_editForm = DTMLFile('dtml/fileEdit',globals(), Kind='File',kind='file')
    manage_editForm._setName('manage_editForm')
    manage = manage_main = manage_editForm
    manage_uploadForm = manage_editForm

    manage_options=(
        (
        {'label':'Edit', 'action':'manage_main',
         'help':('OFSP','File_Edit.stx')},
        {'label':'View', 'action':'',
         'help':('OFSP','File_View.stx')},
        )
        + SimpleItem.manage_options
        )

    __ac_permissions__=(
        ('View management screens',
         ('manage', 'manage_main',)),
        ('Change Images and Files',
         ('manage_edit','manage_upload','PUT')),
        ('View',
         ('index_html', 'view_image_or_file', 'get_size',
          'getContentType', 'PrincipiaSearchSource', '')),
        ('FTP access',
         ('manage_FTPstat','manage_FTPget','manage_FTPlist')),
        ('Delete objects',
         ('DELETE',)),
        )

    _properties=({'id':'title', 'type': 'string'},
                 {'id':'alt', 'type':'string'},
                 {'id':'content_type', 'type':'string'},
                 )

    def __init__(self, id, title, file, content_type='', precondition=''):
        self.__name__ = id
        self.title = title
        self.precondition = precondition
        self.blob = Blob()

        blob = self._read_data(file)
        content_type = self._get_content_type(file, blob, id, content_type)
        self.update_data(blob, content_type)

    def id(self):
        return self.__name__

    def index_html(self, REQUEST, RESPONSE):
        """
        The default view of the contents of a File or Image.

        Returns the contents of the file or image.  Also, sets the
        Content-Type HTTP header to the objects content type.
        """

        if self.precondition and hasattr(self, str(self.precondition)):
            # Grab whatever precondition was defined and then
            # execute it.  The precondition will raise an exception
            # if something violates its terms.
            c=getattr(self, str(self.precondition))
            if hasattr(c, 'isDocTemp') and c.isDocTemp:
                # DTML thingy
                c(REQUEST['PARENTS'][1], REQUEST)
            else:
                c()

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
        RESPONSE.setHeader('Content-Type', self.content_type)
        RESPONSE.setHeader('Content-Length', self.size)

        return self.getIterator()

    def view_image_or_file(self, URL1):
        """
        The default view of the contents of the File or Image.
        """
        raise Redirect, URL1

    def PrincipiaSearchSource(self):
        """ Allow file objects to be searched.
        """
        return ''

    # private
    update_data__roles__=()
    def update_data(self, blob, content_type=None):
        if content_type is not None:
            self.content_type = content_type
        self.blob = blob
        blobh = blob.open("rb")
        blobh.seek(0, 2)
        self.size = blobh.tell()
        blobh.close()

    def manage_edit(self, title, content_type, precondition='',
                    filedata=None, REQUEST=None):
        """
        Changes the title and content type attributes of the File or Image.
        """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        self.title = str(title)
        self.content_type = str(content_type)
        if precondition:
            self.precondition = str(precondition)
        elif self.precondition:
            del self.precondition
        if filedata is not None:
            self.update_data(filedata, content_type)
        if REQUEST:
            message="Saved changes."
            return self.manage_main(self,REQUEST,manage_tabs_message=message)

    def manage_upload(self,file='',REQUEST=None):
        """
        Replaces the current contents of the File or Image object with file.

        The file or images contents are replaced with the contents of 'file'.
        """
        if self.wl_isLocked():
            raise ResourceLockedError, "File is locked via WebDAV"

        blob = self._read_data(file)
        content_type=self._get_content_type(file, blob, self.__name__,
                                            'application/octet-stream')
        self.update_data(blob, content_type)

        if REQUEST:
            message="Saved changes."
            return self.manage_main(self,REQUEST,manage_tabs_message=message)

    def _get_content_type(self, file, blob, id, content_type=None):
        default = content_type

        # Check headers
        headers = getattr(file, 'headers', {})
        content_type = headers.get('content-type', None)

        if content_type is None:
            filename = getattr(file, 'filename', id)
            content_type, enc = mimetypes.guess_type(filename)

        return content_type or default

    def _read_data(self, data):
        """Convert the uploaded data structure into a blob.
        
        Returns a blob instance."""
        if hasattr(self, 'blob'):
            blob = self.blob
        else:
            blob = Blob()
        blobfile = blob.open("wb")
 
        if isinstance(data, str):
            # Big string: cut it into smaller chunks
            blobfile.write(data)
        elif isinstance(data, FileUpload) and not data:
            raise ValueError, 'File not specified'
        elif isinstance(data, FileUpload) or isinstance(data, file):
            while True:
                chunk = data.read(1<<16)
                if not chunk:
                    break
                blobfile.write(chunk)
        elif isinstance(data, Pdata):
            chunk = Pdata
            while chunk is not None:
                blobfile.write(chunk.data)
                chunk = chunk.next
        else:
            raise ValueError, 'Invalid data structure passed. Supported are: Files, Strings, Pdata'
    
        blobfile.close()
        return blob

    def PUT(self, REQUEST, RESPONSE):
        """Handle HTTP PUT requests"""
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        type=REQUEST.get_header('content-type', None)

        file=REQUEST['BODYFILE']

        blob = self._read_data(file)
        content_type = self._get_content_type(file, blob, self.__name__,
                                            type or self.content_type)
        self.update_data(blob, content_type)

        RESPONSE.setStatus(204)
        return RESPONSE

    def getSize(self):
        """Get the size of a file or image.

        Returns the size of the file or image.
        """
        return self.size

    def getContentType(self):
        """Get the content type of a file or image.

        Returns the content type (MIME type) of a file or image.
        """
        return self.content_type

    def __len__(self):
        return 1

    def manage_FTPget(self):
        """Return body for ftp."""
        return self.getIterator()

    def getIterator(self):
        fn = self.blob._current_filename()
        return filestream_iterator(fn)

def cookId(id, title, file):
    if not id and hasattr(file,'filename'):
        filename=file.filename
        title=title or filename
        id=filename[max(filename.rfind('/'),
                        filename.rfind('\\'),
                        filename.rfind(':'),
                        )+1:]
    return id, title

