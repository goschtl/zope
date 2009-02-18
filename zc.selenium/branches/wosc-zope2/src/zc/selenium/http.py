#############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

import cgi
import errno
import BaseHTTPServer
import socket
import threading
import zc.selenium.selenium
import zope.pagetemplate.pagetemplatefile

class DictTemplateFile(zope.pagetemplate.pagetemplatefile.PageTemplateFile):
    """A pagetemplate that accepts arbitrary keyword arguments."""

    def pt_getContext(self, *args, **kw):
        context = super(DictTemplateFile, self).pt_getContext(*args, **kw)
        kw = args[1].copy()
        if kw:
            kw.pop('args', None)
            kw.pop('options', None)
        context.update(kw)
        return context


class QueuePOSTHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    template = DictTemplateFile('results.pt')

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        request = dict([(key, form.getvalue(key)) for key in form.keys()])
        zc.selenium.selenium.messages.put(request)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.template(request=request))

    def log_message(self, *args, **kw):
        # be silent
        pass


class ServerThread(threading.Thread):

    def __init__(self, port):
        super(ServerThread, self).__init__()
        self.setDaemon(True)
        self.port = port

    def run(self):
        self.server = BaseHTTPServer.HTTPServer(('', self.port),
                                                QueuePOSTHandler)
        self.server.serve_forever()
