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
"""SFTP Handler for urllib2

$Id$
"""

import cStringIO, getpass, re, stat, sys, urllib, urllib2
import paramiko

parse_host = re.compile(
    '(?:' '([^@:]+)(?::([^@]*))?@' ')?'
    '([^:]*)(?::(\d+))?$').match

class Result:

    def __init__(self, fp, url, info):
        self._fp = fp
        self.url = url
        self.headers = info

    def geturl(self):
        return self.url

    def info(self):
        return self.headers

    def __getattr__(self, name):
        return getattr(self._fp, name)

class SFTPHandler(urllib2.BaseHandler):

    def sftp_open(self, req):        
        host = req.get_host()
        if not host:
            raise IOError, ('sftp error', 'no host given')

        parsed = parse_host(host)
        if not parsed:
            raise IOError, ('sftp error', 'invalid host', host)
            
        user, pw, host, port = parsed.groups()

        if user:
            user = urllib.unquote(user)
        else:
            user = getpass.getuser()

        if port:
            port = int(port)
        else:
            port = 22

        if pw:
            pw = urllib.unquote(pw)

        host = urllib.unquote(host or '')
        
        trans = paramiko.Transport((host, port))
        if pw is not None:
            trans.connect(username=user, password=pw)
        else:
            for key in paramiko.Agent().get_keys():
                try:
                    trans.connect(username=user, pkey=key)
                    break
                except paramiko.AuthenticationException:
                    pass                
            else:
                raise paramiko.AuthenticationException(
                    "Authentication failed.")

        sftp = paramiko.SFTPClient.from_transport(trans)

        path = req.get_selector()
        url = req.get_full_url()
        mode = sftp.stat(path).st_mode
        if stat.S_ISDIR(mode):
            return Result(
                cStringIO.StringIO('\n'.join([
                    ('<a href="%s/%s">%s</a><br />'
                     % (url, x, x)
                     )
                    for x in sftp.listdir(path)
                    ])),
                url, {'Content-Type': 'text/html'})
        else:
            return Result(sftp.open(path), url, {})

urllib2.install_opener(urllib2.build_opener(SFTPHandler))
        
