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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import sys, unittest, warnings, os
import doctest
from zope.testing.doctest import DocFileSuite
import zc.winauth.winauth


class FakeHandle:
    def __init__(self, sid):
        self.sid = sid

    def Close(self):
        pass


class FakeError:
    def __init__(self, *args):
        self.args = args

    def __getitem__(self, index):
        return self.args[index]


class FakeWin32netcon:
    FILTER_NORMAL_ACCOUNT = 0


class FakeWin32security:
    LOGON32_LOGON_NETWORK = 1
    LOGON32_PROVIDER_DEFAULT = 2
    TokenUser = 3
    all_logins_are_bad = False

    def LogonUser(self, userName, domain, password, logonType, logonProvider):
        # if we are currently dis-allowing all logins...
        if self.all_logins_are_bad:
            raise pywintypes.error(1326)

        if userName == 'jdoe' and password == 'pass':
            return FakeHandle(sid='S-1-5-1')
        elif userName == 'error':
            raise pywintypes.error(999999999)
        else:
            raise pywintypes.error(1326)

    def GetTokenInformation(self, handle, token_type):
        return [handle.sid]

    def ConvertSidToStringSid(self, sid):
        return sid

    def GetBinarySid(self, sid):
        if sid.startswith('S-'):
            return sid
        else:
            raise ValueError

    def LookupAccountSid(self, domain, sid):
        assert domain is None
        if sid == 'S-1-5-1':
            return ['jdoe']
        if sid == 'S-1-5-2':
            return ['jsmith']
        raise RuntimeError('uknown SID "%s"' % sid)

    def LookupAccountName(self, domain, name):
        assert domain is None
        if name == 'jdoe':
            return ['S-1-5-1']
        if name == 'jsmith':
            return ['S-1-5-2']
        if name == 'extra':
            return ['S-1-5-3']
        raise RuntimeError('uknown name "%s"' % name)


class FakePywintypes:
    error = FakeError


class FakeWin32net:
    dc_is_dead = False

    def NetUserGetInfo(self, server, username, *args):
        if username == 'jdoe':
            return {'name': username, 'full_name': u'John Doe'}
        elif username == 'jsmith':
            return {'name': username, 'full_name': u''}
        else:
            raise pywintypes.error(1326)

    def NetGetDCName(self, *args):
        if self.dc_is_dead:
            raise FakeError(999999999)
        return 'DomainControllerName'

    def NetServerGetInfo(self, *args):
        if self.dc_is_dead:
            raise FakeError(999999999)

    def NetUserEnum(self, server, level, filter, handle, prefLen=None):
        if handle == 0:
            data = [self.NetUserGetInfo(server, username)
                    for username in ['jdoe', 'jsmith']]
            return data, len(data)+1, 1
        else:
            data = [{'name': 'extra', 'full_name': 'Extra Guy'}]
            return data, len(data)+1, 0


def setUp(test):
    # set up some fake modules
    global pywintypes
    global win32net
    pywintypes = zc.winauth.winauth.pywintypes = FakePywintypes()
    win32net = zc.winauth.winauth.win32net = FakeWin32net()
    win32security = zc.winauth.winauth.win32security = FakeWin32security()
    zc.winauth.winauth.win32netcon = FakeWin32netcon()
    test.globs['win32net'] = win32net
    test.globs['win32security'] = win32security

def tearDown(test):
    global pywintypes
    global win32net
    # remove the fake modules
    if sys.platform.startswith('win'):
        import pywintypes, win32security, win32net, win32netcon
        zc.winauth.winauth.pywintypes = pywintypes
        zc.winauth.winauth.win32security = win32security
        zc.winauth.winauth.win32net = win32net
        zc.winauth.winauth.win32netcon = win32netcon
    else:
        del pywintypes
        del win32net
        del zc.winauth.winauth.pywintypes
        del zc.winauth.winauth.win32security
        del zc.winauth.winauth.win32net

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(DocFileSuite('README.txt', setUp=setUp, tearDown=tearDown,
                  optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
        ))

    if sys.platform.startswith('win') and 'FIPS_DEVEL_MODE' not in os.environ:
        wap = zc.winauth.winauth.WindowsAuthenticationPlugin()

        # if it appears that the test user has been configured, do the
        # integration tests
        import pywintypes, win32net
        try:
            win32net.NetGetDCName(None, None)
        except pywintypes.error, e:
            warnings.warn('this machine is apparently not part of a domain;'
                          ' Windows authentication tests are being skipped.')
        else:
            if wap.searchUsers('Testy Testerson', 0, 10):
                suite.addTest(DocFileSuite('integration.txt',
                    optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS))
            else:
                warnings.warn('The test user is not set up; Windows'
                              ' authentication tests are being skipped.')
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
