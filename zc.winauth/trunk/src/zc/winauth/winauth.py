##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Windows Authentication Plugin."""
import sys, logging, time, re

import persistent

from zope import interface
from zope.location.interfaces import ILocation
import zope.app.authentication
import zope.app.authentication.interfaces
import zope.app.error.interfaces

import zc.security.interfaces
import zc.winauth.interfaces

BAD_CREDENTIALS_TIMEOUT = 30

if sys.platform.startswith('win'):
    import pywintypes, win32security, win32net, win32netcon
    import pythoncom, win32api
    from win32com.client import GetObject
    from win32com.client.gencache import EnsureDispatch


class PrincipalInfo(object):
    interface.implements(
        zope.app.authentication.interfaces.IPrincipalInfo,
        zc.winauth.interfaces.IUserInfo)

    def __init__(self, id, title, description='', name=''):
        self.id = id
        self.title = title
        self.description = description
        self.name = name


class WindowsAuthenticationPlugin(persistent.Persistent):
    interface.implements(
        zope.app.authentication.interfaces.IAuthenticatorPlugin,
        zc.security.interfaces.ISimpleUserSearch,
        ILocation) # TODO remove this

    __name__ = __parent__ = None
    _server = None
    prefix = 'zc.winauth'
    last_bad_credentials = None
    last_bad_time = 0

    def __init__(self):
        assert win32security

    def authenticateCredentials(self, credentials):
        if credentials is None:
            return

        if (time.time() - self.last_bad_time < BAD_CREDENTIALS_TIMEOUT and
            credentials == self.last_bad_credentials):
            return

        # this if is to prevent a write-on-read
        if self.last_bad_credentials is not None:
            self.last_bad_credentials = None
            self.last_bad_time = 0

        username = credentials['login']
        password = credentials['password']

        logging.info('Begining authentication for "%s".' % username)
        info = None
        uid = self.checkPassword(username, password)
        if uid is None:
            self.last_bad_credentials = credentials
            self.last_bad_time = time.time()
        else:
            info = self.principalInfo(self.prefix + '.' + uid)

        logging.info('Done with authentication for "%s".' % username)
        return info

    # For this method to work, the user running the code requires the
    # privilege to "Act as part of the Operating System" (SE_TCB_NAME)
    # on Windows 2000 (but not XP or 2003).  To add it go to Control Panel/
    # Administrative Tools/Local Security Policy.  Expand Local Policies
    # and choose User Rights Assignment.  Double-click on "Act as part of
    # the operating system" and add the desired user.  The user must log
    # out and back in for the new privilege to take effect.
    def checkPassword(self, username, password):
        logging.info('Authenticating credentials for "%s".' % username)
        try:
            handle=win32security.LogonUser(username, None, password,
                          # We use LOGON32_LONGON_NETWORK because it's faster.
                          win32security.LOGON32_LOGON_NETWORK,
                          win32security.LOGON32_PROVIDER_DEFAULT)

            sid = win32security.GetTokenInformation(handle,
                                                    win32security.TokenUser)[0]
            # we got back a binary SID, we want a string representation
            sid = win32security.ConvertSidToStringSid(sid)
            # We're not going to use the handle, just seeing if we can get it.
            handle.Close()
        except pywintypes.error, e:
            # Because of the sheer number of windows-specific errors that can
            # occur here, we have to assume any of them mean that the
            # credentials were not valid.

            # log the exception
            logging.warning('An exception occurred while attempting to '
                            'authenticate the user "%s".' % username,
                            exc_info=sys.exc_info())
            # something bad happened, so the user can't be authenticated
            result = None
        else:
            result = sid


        logging.info('Done authenticating credentials for "%s".' % username)
        return result

    def principalInfo(self, id):
        if not id.startswith(self.prefix+'.'):
            return

        string_sid = id[len(self.prefix)+1:]

        try:
            sid = win32security.GetBinarySid(string_sid)
        except ValueError:
            return None

        username = win32security.LookupAccountSid(None, sid)[0]

        while True:
            try:
                # try to use the current server to get user info
                info = win32net.NetUserGetInfo(self.server, username, 10)
            except pywintypes.error, e:
                # Because of the sheer number of windows-specific errors
                # that can occur here, we have to assume any of them mean
                # that the user's info couldn't be retrieved.

                # log the exception
                logging.warning('An exception occurred while attempting '
                                'to get information about the user "%s".'
                                % username, exc_info=sys.exc_info())
                # something bad happened, so the user's info can't be retrieved
                return
            break

        title = info['full_name']
        if not title:
            title = username
        description = info.get('comment') or ''
        name = info.get('name') or ''

        return PrincipalInfo(id, title, description, name)

    @property
    def server(self):
        while True:
            if self._server is None:
                try:
                    self._server = win32net.NetGetDCName(None, None)
                except pywintypes.error:
                    logging.warn('An exception occurred while attempting '
                                 'to contact a domain controller.',
                                 exc_info=sys.exc_info())
                    raise

            try:
                # make sure the server is still alive, if it is, this won't
                # raise an exception
                win32net.NetServerGetInfo(self._server, 100)
            except pywintypes.error:
                # the server appears to be down, forget it's name and try again
                self._server = None
                logging.warn('The domain controller went away, will try to '
                             'find another one.', exc_info=sys.exc_info())
                continue
            break
        return self._server

    def searchUsers(self, filter, start, size):
        def getSid(username):
            sid = win32security.LookupAccountName(None, username)[0]
            sid = win32security.ConvertSidToStringSid(sid)
            return sid

        def getConnection():
            connection = EnsureDispatch('ADODB.Connection')
            connection.Provider = 'ADsDSOObject'
            connection.Open('Active Directory Provider')
            return connection

        def query(query_string):
            command = EnsureDispatch('ADODB.Command')
            command.ActiveConnection = getConnection()
            command.CommandText = query_string

            recordset, result = command.Execute()
            while not recordset.EOF:
                yield GetObject(str(recordset.Fields.Item(0)))
                recordset.MoveNext()

        def buildWhere(filter):
            chunks = filter.strip().split(' ')
            chunks = ["displayName='*%s*'" % chunk for chunk in chunks]
            return ' and '.join(chunks)

        def filterIsSafe(filter):
            return re.match(r'^(\w|\s)*$', filter)

        if not filterIsSafe(filter):
            return []

        pythoncom.CoInitialize()
        results = []
        domain_name = win32api.GetDomainName()
        root = GetObject('LDAP://%s/rootDSE' % domain_name)
        dnc = root.Get('defaultNamingContext')
        ADsPath = GetObject('LDAP://%s/%s' % (domain_name, dnc)).ADsPath

        where = "objectCategory = 'Person'"

        if filter.strip():
            where = where + 'and ' + buildWhere(filter)

        for user in query("select * from '%s' where %s" % (ADsPath, where)):
            if user.sAMAccountName:
                results.append(self.prefix + '.' + getSid(user.sAMAccountName))

            # see if we've found enough to stop
            if len(results) >= start + size:
                break

        return results[start:start+size]
