##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""HTTP server factories

$Id$
"""

from cStringIO import StringIO
import tempfile

from twisted.web2 import iweb, log, resource, server, stream, wsgi
from twisted.web2.channel.http import HTTPFactory

from zope.app.twisted.server import ServerType, SSLServerType
from zope.app.wsgi import WSGIPublisherApplication
from zope.app.wsgi import PMDBWSGIPublisherApplication

max_stringio = 100*1000 # Should this be configurable?

class Prebuffer(resource.WrapperResource):

    def hook(self, req):
        content_length = req.stream.length

        if content_length > max_stringio:
            temp = tempfile.TemporaryFile()
            def done(_):
                temp.seek(0)
                # Replace the request's stream object with the tempfile
                req.stream = stream.FileStream(temp, useMMap=False)
                # Hm, this shouldn't be required:
                req.stream.doStartReading = None
        else:
            temp = StringIO()
            def done(_):
                # Replace the request's stream object with the tempfile
                req.stream = stream.MemoryStream(temp.getvalue())
                # Hm, this shouldn't be required:
                req.stream.doStartReading = None

        return stream.readStream(req.stream, temp.write).addCallback(done)


def createHTTPFactory(db):
    resource = wsgi.WSGIResource(WSGIPublisherApplication(db))
    resource = log.LogWrapperResource(resource)
    resource = Prebuffer(resource)

    return HTTPFactory(server.Site(resource))

http = ServerType(createHTTPFactory, 8080)
https = SSLServerType(createHTTPFactory, 8443)


def createPMHTTPFactory(db):
    resource = wsgi.WSGIResource(PMDBWSGIPublisherApplication(db))
    resource = log.LogWrapperResource(resource)
    resource = Prebuffer(resource)

    return HTTPFactory(server.Site(resource))

pmhttp = ServerType(createPMHTTPFactory, 8080)
