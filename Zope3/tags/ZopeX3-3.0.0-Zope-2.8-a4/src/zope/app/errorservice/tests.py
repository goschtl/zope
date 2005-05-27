##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Error Reporting Service Tests

$Id$
"""
import sys
from unittest import TestCase, TestLoader, TextTestRunner
from zope.app.errorservice import ErrorReportingService
from zope.testing.cleanup import CleanUp
from zope.exceptions.exceptionformatter import format_exception
from zope.publisher.tests.httprequest import TestRequest


class C1(object):
    def getAnErrorInfo(self):
        exc_info = None
        try:
            someerror()
        except:
            exc_info = sys.exc_info()
        return exc_info


class ErrorReportingServiceTests(CleanUp, TestCase):
    def test_checkForEmpryLog(self):
        # Test Check Empty Log
        errService = ErrorReportingService()
        getProp = errService.getLogEntries()
        self.failIf(getProp)

    def test_checkProperties(self):
        # Test Properties test
        errService = ErrorReportingService()
        setProp = {
            'keep_entries':10,
            'copy_to_zlog':1,
            'ignored_exceptions':()
            }
        errService.setProperties(**setProp)
        getProp = errService.getProperties()
        self.assertEqual(setProp, getProp)

    def test_ErrorLog(self):
        # Test for Logging Error.  Create one error and check whether its
        # logged or not.
        errService = ErrorReportingService()
        exc_info = C1().getAnErrorInfo()
        errService.raising(exc_info)
        getErrLog = errService.getLogEntries()
        self.assertEquals(1, len(getErrLog))

        tb_text = ''.join(format_exception(*exc_info, **{'as_html': 0}))

        err_id =  getErrLog[0]['id']
        self.assertEquals(tb_text,
                          errService.getLogEntryById(err_id)['tb_text'])

    def test_ErrorLog_Unicode_urls(self):
        # Emulate a unicode url, it gets encoded to utf-8 before it's passed
        # to the request. Also add some unicode field to the request's
        # environment
        request = TestRequest(environ={'PATH_INFO': '/\xd1\x82',
                                       'SOME_UNICODE': u'\u0441'})
        errService = ErrorReportingService()
        exc_info = C1().getAnErrorInfo()
        errService.raising(exc_info, request=request)
        getErrLog = errService.getLogEntries()
        self.assertEquals(1, len(getErrLog))

        tb_text = ''.join(format_exception(*exc_info, **{'as_html': 0}))

        err_id =  getErrLog[0]['id']
        self.assertEquals(tb_text,
                          errService.getLogEntryById(err_id)['tb_text'])
        

def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(ErrorReportingServiceTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
