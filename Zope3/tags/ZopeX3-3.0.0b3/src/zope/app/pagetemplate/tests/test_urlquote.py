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
"""URLQuote Tests

I kept the tests quite small, just covering that the functions actually do
something (and don't really scramble stuff). We are relying on the python urllib
to be functional to avoid test duplication.

$Id: test_talesapi.py 25177 2004-06-02 13:17:31Z jim $
"""

from zope.testing.doctestunit import DocTestSuite
from zope.app.pagetemplate.urlquote import URLQuote


class TestObject(object):

    def __str__(self):
        return "www.google.de"

def quote_simple():
    """
    >>> q = URLQuote(u"www.google.de")
    >>> q.quote()
    u'www.google.de'
    >>> q.unquote()
    u'www.google.de'
    >>> q.quote_plus()
    u'www.google.de'
    >>> q.unquote_plus()
    u'www.google.de'
    """

def quote_cast_needed():
    """
    >>> q = URLQuote(TestObject())
    >>> q.quote()
    'www.google.de'
    >>> q.unquote()
    'www.google.de'
    >>> q.quote_plus()
    'www.google.de'
    >>> q.unquote_plus()
    'www.google.de'
    """

def test_suite():
    return DocTestSuite()

if __name__ == '__main__':
    unittest.main()
