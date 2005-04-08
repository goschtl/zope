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
"""File views.

$Id$
"""

from datetime import datetime

import zope.event

from zope.app import content_types
from zope.app.event import objectevent
from zope.app.file.file import File
from zope.app.i18n import ZopeMessageIDFactory as _

__docformat__ = 'restructuredtext'


class FileView(object):

    def show(self):
        """Call the File"""
        request = self.request
        if request is not None:
            request.response.setHeader('Content-Type',
                                       self.context.contentType)
            request.response.setHeader('Content-Length',
                                       self.context.getSize())

        return self.context.data


class FileUpdateView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def errors(self):
        form = self.request.form
        if "UPDATE_SUBMIT" in form:
            filename = getattr(form["field.data"], "filename", None)
            contenttype = form.get("field.contentType")
            if filename:
                if not contenttype:
                    contenttype = content_types.guess_content_type(filename)[0]
                if not form.get("add_input_name"):
                    form["add_input_name"] = filename
            return self.update_object(form["field.data"], contenttype)
        return ''


class FileAdd(FileUpdateView):
    """View that adds a new File object based on a file upload.

    >>> class FauxAdding(object):
    ...     def add(self, content):
    ...         self.content = content
    ...     def nextURL(self):
    ...         return 'next url'

    >>> from zope.publisher.browser import TestRequest
    >>> import StringIO
    >>> sio = StringIO.StringIO("some data")
    >>> sio.filename = 'abc.txt'

    Let's make sure we can use the uploaded file name if one isn't
    specified by the user, and can use the content type when
    specified.

    >>> request = TestRequest(form={'field.data': sio,
    ...                             'field.contentType': 'text/foobar',
    ...                             'UPDATE_SUBMIT': 'Add'})
    >>> adding = FauxAdding()
    >>> view = FileAdd(adding, request)
    >>> view.errors()
    ''
    >>> adding.content.contentType
    'text/foobar'
    >>> adding.content.data
    'some data'
    >>> request.form['add_input_name']
    'abc.txt'

    Now let's guess the content type, but also use a provided file
    name for adding the new content object:

    >>> request = TestRequest(form={'field.data': sio,
    ...                             'field.contentType': '',
    ...                             'add_input_name': 'splat.txt',
    ...                             'UPDATE_SUBMIT': 'Add'})
    >>> adding = FauxAdding()
    >>> view = FileAdd(adding, request)
    >>> view.errors()
    ''
    >>> adding.content.contentType
    'text/plain'
    >>> request.form['add_input_name']
    'splat.txt'

    """

    def update_object(self, data, contenttype):
        f = File(data, contenttype)
        zope.event.notify(objectevent.ObjectCreatedEvent(f))
        self.context.add(f)
        self.request.response.redirect(self.context.nextURL())
        return ''


class FileUpload(FileUpdateView):
    """View that updates an existing File object with a new upload.

    >>> from zope.publisher.browser import TestRequest
    >>> import StringIO
    >>> sio = StringIO.StringIO("some data")
    >>> sio.filename = 'abc.txt'

    Before we instanciate the request, we need to make sure that the
    ``IUserPreferredLanguages`` adapter exists, so that the request's
    locale exists.  This is necessary because the ``update_object``
    method uses the locale formatter for the status message:

    >>> from zope.app.testing import ztapi
    >>> from zope.publisher.browser import BrowserLanguages
    >>> from zope.publisher.interfaces.http import IHTTPRequest
    >>> from zope.i18n.interfaces import IUserPreferredLanguages
    >>> ztapi.provideAdapter(IHTTPRequest, IUserPreferredLanguages,
    ...                      BrowserLanguages)

    Let's make sure we can use the uploaded file name if one isn't
    specified by the user, and can use the content type when
    specified.

    >>> request = TestRequest(form={'field.data': sio,
    ...                             'field.contentType': 'text/foobar',
    ...                             'UPDATE_SUBMIT': 'Update'})
    >>> file = File()
    >>> view = FileUpload(file, request)
    >>> view.errors()
    u'Updated on ${date_time}'
    >>> file.contentType
    'text/foobar'
    >>> file.data
    'some data'

    Now let's guess the content type, but also use a provided file
    name for adding the new content object:

    >>> request = TestRequest(form={'field.data': sio,
    ...                             'field.contentType': '',
    ...                             'add_input_name': 'splat.txt',
    ...                             'UPDATE_SUBMIT': 'Update'})
    >>> file = File()
    >>> view = FileUpload(file, request)
    >>> view.errors()
    u'Updated on ${date_time}'
    >>> file.contentType
    'text/plain'
    """

    def update_object(self, data, contenttype):
        self.context.contentType = contenttype
        self.context.data = data
        formatter = self.request.locale.dates.getFormatter(
            'dateTime', 'medium')
        status = _("Updated on ${date_time}")
        status.mapping = {'date_time': formatter.format(datetime.utcnow())}
        return status
