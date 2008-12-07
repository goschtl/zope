##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""zope.release tools tests

$Id$
"""
__docformat__ = 'restructuredtext'
import os
import pickle
import unittest
import urllib2
import xmlrpclib
from StringIO import StringIO

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite


class FakeServer(object):
    """Pretend Cheeseshop XML-RPC server."""

    url_data = {
        ('z3c.formdemo', '1.1.0'): [
            dict(url="http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.1.0-py2.4.egg",
                 md5_digest="9d605bd559ea33ac57ce11f5c80fa3d3",
                 filename="z3c.formdemo-1.1.0-py2.4.egg"),
            dict(url="http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.1.0.tar.gz",
                 md5_digest="f224a49cea737112284f74b859e3eed0",
                 filename="z3c.formdemo-1.1.0.tar.gz"),
        ],
        ('zope.component', '3.4.0'): [
            dict(url="http://pypi.python.org/packages/2.4/z/zope.component/zope.component-3.4.0-py2.4.egg",
                 md5_digest="c0763e94912e4a8ac1e321a068c916ba",
                 filename="zope.component-3.4.0-py2.4.egg"),
            dict(url="http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4.0.tar.gz",
                 md5_digest="94afb57dfe605d7235ff562d1eaa3bed",
                 filename="zope.component-3.4.0.tar.gz"),
        ],
        ('zope.interface', '3.4.0'): [
            dict(url="http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.4.0.tar.gz",
                 md5_digest="0be9fd80b7bb6bee520e56eba7d29c90",
                 filename="zope.interface-3.4.0.tar.gz"),
            dict(url="http://pypi.python.org/packages/2.4/z/zope.interface/zope.interface-3.4.0-py2.4-win32.egg",
                 md5_digest="3fa5e992271375eac597622d8e2fd5ec",
                 filename="zope.interface-3.4.0-py2.4-win32.egg"),
        ],
        ('zope.interface', '3.4.1'): [
            dict(url="http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.4.1.tar.gz",
                 md5_digest="b085f4a774adab688e037ad32fbbf08e",
                 filename="zope.interface-3.4.1.tar.gz"),
        ],
    }

    releasedata = None

    def __init__(self, url):
        self.releasedata = pickle.load(
            open(os.path.join(os.path.dirname(__file__),
                              'release_data.dat'), 'r'))

    def package_urls(self, package_name, version):
        return self.url_data.get((package_name, version), [])

    def release_data(self, package_name, version):
        return self.releasedata.get((package_name, version), [])


testpages = {

    'http://cheeseshop.python.org/simple/PIL/': '''\
<html><head><title>Links for PIL</title></head><body><h1>Links for PIL</h1><a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.5 home_page</a><br/>
<a href='http://effbot.org/zone/pil-changes-115.htm' rel="download">1.1.5 download_url</a><br/>
<a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.5a2 home_page</a><br/>
<a href='http://effbot.org/zone/pil-changes-115.htm' rel="download">1.1.5a2 download_url</a><br/>
<a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.5a1 home_page</a><br/>
<a href='http://effbot.org/zone/pil-changes-115.htm' rel="download">1.1.5a1 download_url</a><br/>
<a href='http://www.pythonware.com/products/pil/' rel="homepage">1.1.4 home_page</a><br/>
<a href='http://www.pythonware.com/products/pil/' rel="homepage">1.1.3 home_page</a><br/>
<a href='http://www.pythonware.com/downloads/Imaging-1.1.3.tar.gz' rel="download">1.1.3 download_url</a><br/>
<a href='http://www.pythonware.com/products/pil' rel="homepage">1.1.6 home_page</a><br/>
<a href='http://effbot.org/downloads/#Imaging' rel="download">1.1.6 download_url</a><br/>
</body></html>''',

    'http://cheeseshop.python.org/simple/z3c.formdemo/': '''\
<html><head><title>Links for z3c.formdemo</title></head><body><h1>Links for z3c.formdemo</h1><a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.3.0b1 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.0.0 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.2.0 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.3.0 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.0.0c1 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.0.0c2 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.1.0 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.1.1 home_page</a><br/>
<a href='http://svn.zope.org/z3c.formdemo' rel="homepage">1.1.2 home_page</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.4.0-py2.4.egg#md5=a181256b458c09b43e07357ef42336f4'>z3c.formdemo-1.4.0-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.4.0.tar.gz#md5=b74b3fbd95e5b6098e77c97e82f7f417'>z3c.formdemo-1.4.0.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.5.0.tar.gz#md5=c857c33d6c4aed24d6cd57822ed3969b'>z3c.formdemo-1.5.0.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.0.0-py2.4.egg#md5=7c53ed6db7b319a3ba5540f74dcf728e'>z3c.formdemo-1.0.0-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.3.0-py2.4.egg#md5=334ef296e654a88aab4ed109a4cafd24'>z3c.formdemo-1.3.0-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.1.1-py2.4.egg#md5=2d76656e5732314a8259f568df7d1e42'>z3c.formdemo-1.1.1-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.1.2.tar.gz#md5=870d2f59d448f95bc77748ace576645e'>z3c.formdemo-1.1.2.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.0.0c2-py2.4.egg#md5=176ee4caa26222a89428d4d028b4d6dd'>z3c.formdemo-1.0.0c2-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.0.0c1.tar.gz#md5=befa095c9d48987fba28d66d752248e9'>z3c.formdemo-1.0.0c1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.1.0-py2.4.egg#md5=9d605bd559ea33ac57ce11f5c80fa3d3'>z3c.formdemo-1.1.0-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.5.2.tar.gz#md5=c02d2bf88294c640ea127b814515658d'>z3c.formdemo-1.5.2.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.0.0c2.tar.gz#md5=75d9a26ea296dffad7e25cef9c332c7f'>z3c.formdemo-1.0.0c2.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.3.0b1-py2.4.egg#md5=df9638a8382a0b47e0031a2e176e3037'>z3c.formdemo-1.3.0b1-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.1.1.tar.gz#md5=84d16484a1c1b48507c0f09e4fefe356'>z3c.formdemo-1.1.1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.1.2-py2.4.egg#md5=d47cfed41b4be7ce3cc6c719735c31b9'>z3c.formdemo-1.1.2-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.2.0-py2.4.egg#md5=4adb57710f7aea934f4769ae7fbb585d'>z3c.formdemo-1.2.0-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.3.0.tar.gz#md5=3b341ae84fcb8ee0996cce8126a0074b'>z3c.formdemo-1.3.0.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.2.0.tar.gz#md5=5f3f3dd5c7599c4c8c877e822f642fae'>z3c.formdemo-1.2.0.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.5.1.tar.gz#md5=582dcc2db08b2d3c6564b2cb2e9a4e62'>z3c.formdemo-1.5.1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.1.0.tar.gz#md5=f224a49cea737112284f74b859e3eed0'>z3c.formdemo-1.1.0.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/z3c.formdemo/z3c.formdemo-1.0.0c1-py2.4.egg#md5=8a0bb4deb808c57f57138f3477e40756'>z3c.formdemo-1.0.0c1-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.3.0b1.tar.gz#md5=32afd43b4c9129f8d2d6fb0f55df8e14'>z3c.formdemo-1.3.0b1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/z3c.formdemo/z3c.formdemo-1.0.0.tar.gz#md5=891f63c74ac90e01670d84aba5b724cc'>z3c.formdemo-1.0.0.tar.gz</a><br/>
<a href='http://localhost:8080/'>http://localhost:8080/</a><br/>
<a href='http://localhost:8080/++skin++Z3CFormDemo'>http://localhost:8080/++skin++Z3CFormDemo</a><br/>
</body></html>
    ''',

    'http://cheeseshop.python.org/simple/zope.component/': '''\
<html><head><title>Links for zope.component</title></head><body><h1>Links for zope.component</h1><a href='http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4.0.tar.gz#md5=94afb57dfe605d7235ff562d1eaa3bed'>zope.component-3.4.0.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/zope.component/zope.component-3.4.0-py2.4.egg#md5=c0763e94912e4a8ac1e321a068c916ba'>zope.component-3.4.0-py2.4.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4dev-r72747.tar.gz#md5=f352802dfbc1d1728a30784617976137'>zope.component-3.4dev-r72747.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4dev-r72605.tar.gz#md5=6c7f82343c4008a6cf547fb23227448c'>zope.component-3.4dev-r72605.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4dev-r72749.tar.gz#md5=23625ac9ec78f1098a3bbc7f6bf86ca4'>zope.component-3.4dev-r72749.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.component/zope.component-3.4dev-r72748.tar.gz#md5=fe51ceddb7db4ff7630a91dee4525235'>zope.component-3.4dev-r72748.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.component/zope.component-3.5.1.tar.gz#md5=006c43ad77ed4982e49c07f6e65b68a2'>zope.component-3.5.1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.component/zope.component-3.5.0.tar.gz#md5=9f78c8c3594c27be9d6d84114b237ab3'>zope.component-3.5.0.tar.gz</a><br/>
<a href='http://dev.zope.org/Zope3'>http://dev.zope.org/Zope3</a><br/>
<a href='https://bugs.launchpad.net/zope3/+bug/240631'>https://bugs.launchpad.net/zope3/+bug/240631</a><br/>
<a href='https://bugs.launchpad.net/zope3/+bug/251865'>https://bugs.launchpad.net/zope3/+bug/251865</a><br/>
<a href='http://wiki.zope.org/zope3/LocalComponentManagementSimplification'>http://wiki.zope.org/zope3/LocalComponentManagementSimplification</a><br/>
</body></html>
    ''',

    'http://cheeseshop.python.org/simple/zope.interface/': '''\
<html><head><title>Links for zope.interface</title></head><body><h1>Links for zope.interface</h1><a href='http://pypi.python.org/packages/2.5/z/zope.interface/zope.interface-3.4.0b1-py2.5-win32.egg#md5=3b069b174f33b4cdcc39002c1419bc74'>zope.interface-3.4.0b1-py2.5-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/zope.interface/zope.interface-3.3.0.1-py2.4-win32.egg#md5=ffe64dbc3e16af6648a24160cb649435'>zope.interface-3.3.0.1-py2.4-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/zope.interface/zope.interface-3.4.1-py2.4-win32.egg#md5=e3c6d95903c0c84ffd0a8e1dc1f62619'>zope.interface-3.4.1-py2.4-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/2.5/z/zope.interface/zope.interface-3.3.0-py2.5-win32.egg#md5=d6566db7a7d30790a5f4db541c9a0d25'>zope.interface-3.3.0-py2.5-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/zope.interface/zope.interface-3.4.0-py2.4-win32.egg#md5=3fa5e992271375eac597622d8e2fd5ec'>zope.interface-3.4.0-py2.4-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.4.1.tar.gz#md5=b085f4a774adab688e037ad32fbbf08e'>zope.interface-3.4.1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.3.0.1.tar.gz#md5=9f2388c0f67757e3b2530216a4f29b86'>zope.interface-3.3.0.1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.5/z/zope.interface/zope.interface-3.4.1-py2.5-win32.egg#md5=791ec735bc3639ee80b1ea655edd3655'>zope.interface-3.4.1-py2.5-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.4.0b1.tar.gz#md5=ed711b4da1579ae0c71e2804df2bdc99'>zope.interface-3.4.0b1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.3.0b2.tar.gz#md5=f04b8c2403e3b4a44ac0b083b659a92c'>zope.interface-3.3.0b2.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/zope.interface/zope.interface-3.4.0b1-py2.4-win32.egg#md5=c86504b4f11f949b2c9639276fcadd7a'>zope.interface-3.4.0b1-py2.4-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/2.5/z/zope.interface/zope.interface-3.3.0.1-py2.5-win32.egg#md5=a53bcf1337142c81aedf9899e757c29f'>zope.interface-3.3.0.1-py2.5-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.3.0b1.tar.gz#md5=c49930c7382ebf5143421d2c92d65138'>zope.interface-3.3.0b1.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/2.4/z/zope.interface/zope.interface-3.3.0-py2.4-win32.egg#md5=9eff742b077859f5381d43b15f2723f1'>zope.interface-3.3.0-py2.4-win32.egg</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.3.0.tar.gz#md5=93668855e37b4691c5c956665c33392c'>zope.interface-3.3.0.tar.gz</a><br/>
<a href='http://pypi.python.org/packages/source/z/zope.interface/zope.interface-3.4.0.tar.gz#md5=0be9fd80b7bb6bee520e56eba7d29c90'>zope.interface-3.4.0.tar.gz</a><br/>
</body></html>
    ''',

}


def fake_urlopen(url):
    data = testpages.get(url, '<p>no test data for ' + url + '</p>')
    return StringIO(data)


def setUp(test):
    test.real_urlopen = urllib2.urlopen
    test.real_Server = xmlrpclib.Server
    urllib2.urlopen = fake_urlopen
    xmlrpclib.Server = FakeServer


def tearDown(test):
    urllib2.urlopen = test.real_urlopen


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=(doctest.NORMALIZE_WHITESPACE
                                  |doctest.ELLIPSIS
                                  |doctest.REPORT_NDIFF
                                  |doctest.REPORT_ONLY_FIRST_FAILURE),
                     ),
        ))
