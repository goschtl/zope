##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test TALES 'format' namespace.

$Id: test_formatns.py,v 1.1 2003/09/16 22:18:56 srichter Exp $
"""
import unittest
from datetime import datetime
from zope.publisher.browser import TestRequest
from zope.testing.doctestunit import DocTestSuite
from book.formatns import FormatTalesAPI

class Engine:
    vars = {'request': TestRequest(environ={'HTTP_ACCEPT_LANGUAGE': 'en'})}

def getFormatNamespace(context):
    ns = FormatTalesAPI(context)
    ns.setEngine(Engine())
    return ns


def shortDate():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.shortDate()
    u'9/16/03'
    """
    
def mediumDate():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.mediumDate()
    u'Sep 16, 2003'
    """
    
def longDate():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.longDate()
    u'September 16, 2003'
    """

def fullDate():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.fullDate()
    u'Tuesday, September 16, 2003'
    """

def shortTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.shortTime()
    u'4:51 PM'
    """

def mediumTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.shortTime()
    u'4:51 PM'
    """

def longTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.shortTime()
    u'4:51 PM'
    """

def fullTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.shortTime()
    u'4:51 PM'
    """

def shortDateTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.shortDateTime()
    u'9/16/03 4:51 PM'
    """

def mediumDateTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.mediumDateTime()
    u'Sep 16, 2003 4:51:01 PM'
    """

def longDateTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.longDateTime()
    u'September 16, 2003 4:51:01 PM +000'
    """

def fullDateTime():
    """
    >>> ns = getFormatNamespace(datetime(2003, 9, 16, 16, 51, 01))
    >>> ns.fullDateTime()
    u'Tuesday, September 16, 2003 4:51:01 PM +000'
    """

def decimal():
    """
    >>> ns = getFormatNamespace(4.205)
    >>> ns.decimal()
    u'4.205'
    """

def percent():
    """
    >>> ns = getFormatNamespace(4412)
    >>> ns.percent()
    u'4,412%'
    """

def scientific():
    """
    >>> ns = getFormatNamespace(4421)
    >>> ns.scientific()
    u'4E3'
    """

def currency():
    """
    >>> ns = getFormatNamespace(4.205)
    >>> ns.currency()
    u'\\xa44.21'
    """

def test_suite():
    return DocTestSuite()

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
