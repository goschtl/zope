##############################################################################
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
import getpass
import httplib
import os.path
import socket

import paramiko


class FileSocket(object):
    """
    Adapts a file to the socket interface for use with http.HTTPResponse
    """
    def __init__(self, file):
        self.file = file

    def makefile(self, *args):
        return self.file


class SSHConnection(object):
    """
    SSH connection that implements parts of the httplib.HTTPConnection
    interface
    """
    def __init__(self, host_port, user_passwd=None):
        self.headers = {}
        self.host, self.port = host_port.split(':')
        self.port = int(self.port)

        # if username is specified in URL then use it, otherwise
        # default to local userid
        if user_passwd:
            self.remote_user_name = user_passwd.split(':')[0]
        else:
            self.remote_user_name = getpass.getuser()

    def putrequest(self, method, path):
        # open connection to server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self.transport = paramiko.Transport(sock)
        self.transport.start_client()

        # try to get public key from ssh agent
        agent = paramiko.Agent()
        for key in agent.get_keys():
            try:
                self.transport.auth_publickey(self.remote_user_name, key)
                break
            except paramiko.SSHException:
                pass

        # try to get public key from fs
        if not self.transport.is_authenticated():
            path = os.path.expanduser('~/.ssh/id_rsa')
            try:
                key = paramiko.RSAKey.from_private_key_file(path)
            except paramiko.PasswordRequiredException:
                password = getpass.getpass('RSA key password: ')
                key = paramiko.RSAKey.from_private_key_file(path, password)
            try:
                self.transport.auth_publickey(self.remote_user_name, key)
            except paramiko.SSHException:
                pass

        if not self.transport.is_authenticated():
            path = os.path.expanduser('~/.ssh/id_dsa')
            try:
                key = paramiko.DSSKey.from_private_key_file(path)
            except paramiko.PasswordRequiredException:
                password = getpass.getpass('DSS key password: ')
                key = paramiko.DSSKey.from_private_key_file(path, password)
            try:
                self.transport.auth_publickey(self.remote_user_name, key)
            except paramiko.SSHException:
                raise Exception('No valid public key found')

        # try to get host key
        hostkeytype = None
        hostkey = None
        try:
            host_keys = paramiko.util.load_host_keys(
                os.path.expanduser('~/.ssh/known_hosts'))
        except IOError:
            try:
                # try ~/ssh/ too, because windows can't have a folder
                # named ~/.ssh/
                host_keys = paramiko.util.load_host_keys(
                    os.path.expanduser('~/ssh/known_hosts'))
            except IOError:
                host_keys = {}

        if host_keys.has_key(self.host):
            hostkeytype = host_keys[self.host].keys()[0]
            hostkey = host_keys[self.host][hostkeytype]

        # verify host key
        if hostkey:
            server_key = self.transport.get_server_key()
            if server_key != hostkey:
                raise Exception(
                    "Remote host key doesn't match value in known_hosts")

        # start zsync subsystem on server
        self.channel = self.transport.open_session()
        self.channel.invoke_subsystem('zsync')
        self.channelr = self.channel.makefile('rb')
        self.channelw = self.channel.makefile('wb')

        # start sending request
        self.channelw.write('%s %s\r\n' % (method, path))

    def putheader(self, name, value):
        self.channelw.write('%s: %s\r\n' % (name, value))

    def endheaders(self):
        self.channelw.write('\r\n')

    def send(self, data):
        self.channelw.write(data)

    def getresponse(self):
        response = httplib.HTTPResponse(FileSocket(self.channelr))
        response.begin()
        return response
