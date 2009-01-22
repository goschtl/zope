##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Infrastructure to allow sellenium tests to be written in Python

$Id: pytest.py 13165 2006-08-14 22:33:23Z fred $
"""
import os.path
import sys
import urlparse
import re
from xml.sax.saxutils import escape

import zope.publisher.interfaces.browser

from zope import component, interface


class ISeleniumTest(zope.publisher.interfaces.browser.IBrowserPublisher):
    """A page that is a selenium test."""

    def __call__():
        """Return the selenium test as an HTML string."""


PATTERNS = ()


def selectTestsToRun(patterns):
    """Filter the Selenium tests in the test suite.

    Only tests with names matching any of the regular expressions in the
    list of patterns will be run.

    selectTestsToRun([]) removes any filtering.
    """
    global PATTERNS
    PATTERNS = patterns


def matchesAnyPattern(name, patterns):
    """Check if a test name matches any of the patterns.

        >>> matchesAnyPattern('foobar', ['ab', 'ob'])
        True
        >>> matchesAnyPattern('foobar', ['bo', 'bu'])
        False

    The patterns are regular expressions

        >>> matchesAnyPattern('foobar', ['^f.*ar$'])
        True

    If the pattern list is empty, returns True

        >>> matchesAnyPattern('foobar', [])
        True

    """
    for pattern in patterns:
        if re.search(pattern, name):
            return True
    return not patterns


def suite(request):
    tests = sorted(component.getAdapters([request], ISeleniumTest))
    if PATTERNS:
        tests = [(name, test) for name, test in tests
                 if matchesAnyPattern(name, PATTERNS)]
    return '\n'.join([
        ('<tr><td><a href="/@@/%s">%s</a></td></tr>' % (
             name,
             (test.__doc__ or '').strip().split('\n')[0] or name,
             )
         )
        for name, test in tests
        ])


class Row:

    def __init__(self, output, name, cssClass=''):
        self.output = output
        self.__name__ = name
        self.cssClass = cssClass

    def __call__(self, arg1='', arg2='', lineno=True, frame=None):
        if lineno and self.__name__ != 'comment':
            if frame is None:
                frame = sys._getframe(1)
            filename = frame.f_code.co_filename
            base = os.path.basename(filename)
            comment_arg1 = ('%s:%s <span class="longpath">%s:%d</span>' %
                (base, frame.f_lineno, filename, frame.f_lineno))
            self.raw('comment', comment_arg1, '', cssClass='lineinfo')
        self.raw(self.__name__, escape(unicode(arg1)), escape(unicode(arg2)),
                 self.cssClass)

    def raw(self, name, arg1, arg2, cssClass):
        append = self.output.append

        html_css_class = ("%s %s" % (name, cssClass)).strip()
        append('<tr class="%s">\n<td>' % html_css_class)
        append(name)
        append('</td>\n')
        append('<td>')
        append(arg1)
        append('</td>\n')
        append('<td>')
        append(arg2)
        append('</td>\n')
        append('</tr>\n')


# Moving the embedded stylesheet to a separate file and using @import
# doesn't work for some reason (probably related to the way Selenium
# loads the test).
#
header = """<html>
<head>
<title>%s</title>
<style type="text/css">

.longpath:before {
  content: "(";
  font-size: 90%%;
  }

.longpath {
  font-size: 90%%;
  }

.longpath:after {
  content: ")";
  font-size: 90%%;
  }

</style>
</head>
<body>
<table cellpadding="1" cellspacing="1" border="1">
<tbody>
<tr>
<td rowspan="1" colspan="3">%s</td>
</tr>

"""

footer = '</tbody></table></body></html>'

class Selenium:

    def __init__(self, request, title, message=None):
        if message is None:
            message = title
        self.output = [header % (title, message)]
        url = str(request.URL)
        self.server = urlparse.urlsplit(url)[1]

    def push(self):
        self.open('http://%s/@@/selenium-push.html' % self.server,
                  lineno=False)

    def pop(self):
        self.open('http://%s/@@/selenium-pop.html' % self.server,
                  lineno=False)

    def __getattr__(self, name):
        return Row(self.output, name)

    def __str__(self):
        return ''.join(self.output) + footer

class Test(object):
    component.adapts(zope.publisher.interfaces.browser.IBrowserRequest)
    interface.implements(ISeleniumTest)

    def __init__(self, request):
        self.request = request
        title = (self.__doc__ or '').split('\n')[0]
        mess = ''
        if title:
            mess += '\n<h1>%s</h1>\n' % title
            mess += '<br/>\n'.join((self.__doc__ or '').split('\n')[1:])

        self.selenium = Selenium(self.request, title, mess)

    def browserDefault(self, request):
        return self, ()

    def sharedSetUp(self):
        self.selenium.push()

    def sharedTearDown(self):
        self.selenium.pop()

    def setUp(self):
        self.selenium.push()

    def tearDown(self):
        self.selenium.pop()

    def __call__(self):
        tests = [name for name in dir(self) if name.startswith('test')]
        tests.sort()
        s = self.selenium
        outputDoc(self, self.sharedSetUp.__doc__, 2)
        self.sharedSetUp()
        for test in tests:
            test = getattr(self, test)
            outputDoc(self, test.__doc__, 2)
            outputDoc(self, self.setUp.__doc__, 3)
            self.setUp()
            test()
            outputDoc(self, self.tearDown.__doc__, 3)
            self.tearDown()

        self.sharedTearDown()

        return str(s)


# function to avoid class namespace clutter
def outputDoc(self, doc, level):
    if not doc:
        return
    doc = doc.strip()
    if not doc:
        return

    title = doc.split('\n')[0]
    mess = ''
    if title:
        mess += '\n<h%d>%s</h%d>' % (level, title, level)
        mess += '<br/>\n'.join(doc.split('\n')[1:])

    self.selenium.comment.raw('comment', mess, '', '')
