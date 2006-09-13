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

import cStringIO, getpass, os, re, stat, sys, urllib, urllib2
import paramiko

parse_url_host = re.compile(
    '(?:' '([^@:]+)(?::([^@]*))?@' ')?'
    '([^:]*)(?::(\d+))?$').match

if sys.platform == 'win32':
    import _winreg
    parse_reg_key_name = re.compile('(rsa|dss)2?@22:(\S+)$').match
    def _get_hosts_keys():
        regkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                                 r'Software\SimonTatham\PuTTY\SshHostKeys',
                                 )
        keys = paramiko.HostKeys()
        i = 0
        while 1:
            try:
                name, value, type_ = _winreg.EnumValue(regkey, i)
                i += 1
                value = [long(v, 16) for v in value.split(',')]
                ktype, host = parse_reg_key_name(name).groups()
                if ktype == 'rsa':
                    key = paramiko.RSAKey(vals=value)
                if ktype == 'dss':
                    key = paramiko.DSSKey(vals=value)
                keys.add(host, 'ssh-'+ktype, key)
            except WindowsError:
                break

        return keys

else:

    def _get_hosts_keys():
        return paramiko.HostKeys(os.path.expanduser('~/.ssh/known_hosts'))


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

        parsed = parse_url_host(host)
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

        hostkey = _get_hosts_keys()
        hostkey = hostkey.get(host)
        if hostkey is None:
            raise paramiko.AuthenticationException(
                "No stored host key", host)
        [hostkeytype] = list(hostkey)
        hostkey = hostkey[hostkeytype]

        trans = paramiko.Transport((host, port))
        if pw is not None:
            trans.connect(username=user, password=pw)
        else:
            for key in paramiko.Agent().get_keys():
                try:
                    trans.connect(username=user, pkey=key, hostkey=hostkey)
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
        
