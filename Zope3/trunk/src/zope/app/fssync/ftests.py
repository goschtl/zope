##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Functional fssync tests

$Id: test_fssync.py 40495 2005-12-02 17:51:22Z efge $
"""
import unittest
import os
import shutil
import time
import tempfile
import zope
from cStringIO import StringIO
from zope.testing import doctest
from zope.testing import module
from zope.testing import doctestunit
from zope.app.testing import functional
from zope.testbrowser.testing import PublisherConnection

from zope.fssync import fssync
from zope.fssync import fsutil

from zope.app.fssync.testing import AppFSSyncLayer

checkoutdir = tempfile.mkdtemp(prefix='checkoutdir')
        
class TestNetwork(fssync.Network):
    """A specialization which uses a PublisherConnection suitable for functional doctests.
    """

    def httpreq(self, path, view, datasource=None,
                content_type="application/x-snarf",
                expected_type="application/x-snarf"):
        """Issue an request. This is a overwritten version of the original Network.httpreq
        method that uses a TestConnection as a replacement for httplib connections.
        """
        assert self.rooturl
        if not path.endswith("/"):
            path += "/"
        path += view
        conn = PublisherConnection(self.host_port)
        headers = {}
        if datasource is None:
            method = 'GET'
        else:
            method = 'POST'
            headers["Content-type"] = content_type
            stream = StringIO()
            datasource(stream)
            headers["Content-Length"] = str(stream.tell())
            
        if self.user_passwd:
            if ":" not in self.user_passwd:
                auth = self.getToken(self.roottype,
                                     self.host_port,
                                     self.user_passwd)
            else:
                auth = self.createToken(self.user_passwd)
            headers['Authorization'] = 'Basic %s' % auth
        headers['Host'] = self.host_port
        headers['Connection'] = 'close'

        data = None
        if datasource is not None:
            data = stream.getvalue()
            
        conn.request(method, path, body=data, headers=headers)
        response = conn.getresponse()
         
        if response.status != 200:
            raise fsutil.Error("HTTP error %s (%s); error document:\n%s",
                        response.status, response.reason,
                        self.slurptext(response.content_as_file, response.msg))
        elif expected_type and response.msg["Content-type"] != expected_type:
            raise fsutil.Error(self.slurptext(response.content_as_file, response.msg))
        else:
            return response.content_as_file, response.msg    
    
def setUp(test):
    module.setUp(test, 'zope.app.fssync.fssync_txt')
    if not os.path.exists(checkoutdir):
        os.mkdir(checkoutdir)

def tearDown(test):
    module.tearDown(test, 'zope.app.fssync.fssync_txt')
    shutil.rmtree(checkoutdir)

 
def test_suite():
    
    globs = {'os': os,
            'zope':zope,
            'pprint': doctestunit.pprint,
            'checkoutdir': checkoutdir,
            'PublisherConnection': PublisherConnection,
            'TestNetwork': TestNetwork,
            'sleep': time.sleep}
     
    suite = unittest.TestSuite()
    test = functional.FunctionalDocFileSuite('fssync.txt',
                             setUp=setUp, tearDown=tearDown, globs=globs,
                             optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS)
    test.layer = AppFSSyncLayer
    suite.addTest(test)
    return suite

if __name__ == '__main__': unittest.main()
