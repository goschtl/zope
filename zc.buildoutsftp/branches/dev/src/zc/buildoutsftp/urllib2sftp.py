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

import cStringIO, getpass, logging, mimetypes, os, re, stat, sys
import urllib, urllib2
import paramiko

logger = logging.getLogger(__name__)

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

    def __init__(self, fp, url, info, trans):
        self._fp = fp
        self.url = url
        self.headers = info
        self.__trans = trans

    def __del__(self):
        self.__trans.close()

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

        host_keys = _get_hosts_keys().get(host)
        if host_keys is None:
            raise paramiko.AuthenticationException(
                "No stored host key", host)

        if pw is not None:
            trans = paramiko.Transport((host, port))
            try:
                trans.connect(username=user, password=pw)
            except paramiko.AuthenticationException:
                trans.close()
                raise
        else:
            for key in paramiko.Agent().get_keys():
                trans = paramiko.Transport((host, port))
                try:
                    trans.connect(username=user, pkey=key)
                    break
                except paramiko.AuthenticationException:
                    trans.close()                
            else:
                raise paramiko.AuthenticationException(
                    "Authentication failed.")


        # Check host key
        remote_server_key = trans.get_remote_server_key()
        host_key = host_keys.get(remote_server_key.get_name())
        if host_key != remote_server_key:
            raise paramiko.AuthenticationException(
                "Remote server authentication failed.", host) 

        sftp = paramiko.SFTPClient.from_transport(trans)

        path = req.get_selector()
        url = req.get_full_url()
        logger.debug('sftp get: %s', url)
        mode = sftp.stat(path).st_mode
        if stat.S_ISDIR(mode):
            if logger.getEffectiveLevel() < logging.DEBUG:
                logger.log(1, "Dir %s:\n  %s\n",
                           path, '\n  '.join(sftp.listdir(path)))

            return Result(
                cStringIO.StringIO('\n'.join([
                    ('<a href="%s/%s">%s</a><br />'
                     % (url, x, x)
                     )
                    for x in sftp.listdir(path)
                    ])),
                url, {'content-type': 'text/html'}, trans)
        else:
            mtype = mimetypes.guess_type(url)[0]
            if mtype is None:
                mtype = 'application/octet-stream'
            return Result(sftp.open(path), url, {'content-type': mtype},
                          trans)

