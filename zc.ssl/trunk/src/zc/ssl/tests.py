"""Tests for zc.ssl

$Id$
"""
import unittest
import doctest


class StubSSLWrapper(object):

    def __init__(self, sock, ca_certs=None, cert_reqs=None):
        self.sock = sock
        self.ca_certs = ca_certs
        self.cert_reqs = cert_reqs
        print "sssl(%r, %r, %r)" % (sock, ca_certs, cert_reqs)

    def settimeout(self, timeout):
        print "sssl.settimeout(%r)" % timeout

    def connect(self, hostport):
        print "sssl.connect(%r)" % (hostport, )


def test_suite():
    suite = unittest.TestSuite([
        doctest.DocFileSuite(
        'tests.txt',
        optionflags=doctest.ELLIPSIS),
        ])

    return suite
