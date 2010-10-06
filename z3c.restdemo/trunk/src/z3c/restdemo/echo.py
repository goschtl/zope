##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""REST Echo Demo

$Id$
"""
from z3c.rest import rest
from z3c.traverser import traverser
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile


def fixHeaderName(header):
    header = header[5:]
    parts = [part.capitalize() for part in header.split('_')]
    return '-'.join(parts)

class EchoResource(object):
    pass


class EchoResourceTraverserPlugin(traverser.NameTraverserPlugin):
    traversalName = 'echo'

    def _traverse(self, request, name):
        return EchoResource()


class Echo(rest.RESTView):

    template = ViewPageTemplateFile("echo.pt")

    def GET(self):
        self.path = self.request.environment['REQUEST_URI']
        self.method = self.request.method
        self.protocol = self.request.environment['SERVER_PROTOCOL']
        self.parameters = [
            {'name': name, 'value': value}
            for name, value in sorted(self.request.parameters.items())]
        self.headers = [
            {'name': fixHeaderName(name), 'value': value}
            for name, value in sorted(self.request.environment.items())
            if name.startswith('HTTP_')]
        self.body = self.request.bodyStream.read()
        if self.body:
            self.body = '<![CDATA[\n%s\n]]>' %self.body
        return self.template()

    POST = PUT = DELETE = GET
