#!/usr/bin/env python2.3
##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""XML-RPC Client

$Id: xmlrpc_client.py,v 1.1 2003/07/18 11:55:34 srichter Exp $
"""
import httplib
import xmlrpclib
from code import InteractiveConsole
from base64 import encodestring

class BasicAuthTransport(xmlrpclib.Transport):
    def __init__(self, username=None, password=None, verbose=0):
        self.username=username
        self.password=password
        self.verbose=verbose

    def request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request

        self.verbose = verbose

        h = httplib.HTTP(host)
        h.putrequest("POST", handler)

        # required by HTTP/1.1
        h.putheader("Host", host)

        # required by XML-RPC
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))

        # basic auth
        if self.username is not None and self.password is not None:
            h.putheader("AUTHORIZATION", "Basic %s" %
                        encodestring("%s:%s" % (self.username, self.password)
                                     ).replace("\012", ""))
        h.endheaders()

        if request_body:
            h.send(request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(host + handler,
                                          errcode, errmsg, headers)

        return self.parse_response(h.getfile())


if __name__ == '__main__':
    url = raw_input('Message Board URL [http://localhost:8080/board/]: ')
    if url == '':
        url = 'http://localhost:8080/board/'
    username = raw_input('Username: ')
    password = raw_input('Password: ')
    
    board = xmlrpclib.Server(
        url, transport = BasicAuthTransport(username, password))

    print "The message board is available as 'board'"
    console = InteractiveConsole(locals={'board': board})
    console.interact()
