##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

"""
$Id$
"""

import bobo
import mimetypes
import os
import time
import webob


class Directory:
    """Directory resource"""

    def __init__(self, root, path=None):
        self.root = os.path.abspath(root)+os.path.sep
        self.path = path or root

    @bobo.query('')
    def base(self, bobo_request):
        return bobo.redirect(bobo_request.url + '/')

    @bobo.query('/')
    def index(self):
        links = []
        for name in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, name)):
                name += '/'
            links.append('<a href="%s">%s</a>' % (name, name))
        return """
        <html>
        <head><title>%s</title></head>
        <body>
          %s
        </body>
        </html>
        """ % (self.path[len(self.root):], '<br>\n  '.join(links))

    @bobo.subroute('/:name')
    def traverse(self, request, name):
        path = os.path.abspath(os.path.join(self.path, name))
        if not path.startswith(self.root):
            raise bobo.NotFound
        if os.path.isdir(path):
            return Directory(self.root, path)
        else:
            return File(path)

bobo.scan_class(Directory)


def setCacheControl(response, seconds=86400):
    t = time.time() + seconds
    response.headers['Cache-Control'] = 'public,max-age=%s' % seconds
    response.headers['Expires'] = time.strftime(
        '%a, %d %b %Y %H:%M:%S GMT', time.gmtime(t))


class File:
    """File resource"""

    def __init__(self, path):
        self.path = path

    @bobo.query('')
    def base(self, bobo_request):
        response = webob.Response()
        content_type = mimetypes.guess_type(self.path)[0]
        if content_type is not None:
            response.content_type = content_type
            if not content_type.startswith('text'):
                response.charset = None
        try:
            response.body = open(self.path, 'rb').read()
        except IOError:
            raise bobo.NotFound
        setCacheControl(response)
        response.headers['Last-Modified'] = time.strftime(
            '%a, %d %b %Y %H:%M:%S GMT', time.gmtime(
            float(os.path.getmtime(self.path)) or time()))
        return response

bobo.scan_class(File)

