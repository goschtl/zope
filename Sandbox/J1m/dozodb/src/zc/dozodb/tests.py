##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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

import doctest
import manuel.capture
import manuel.doctest
import manuel.testing
import os
import re
import spidermonkey
import sys
import time
import unittest
import zope.testing.module
import zope.testing.setupstack

baseUrl = None # Set by test runner.

run_time = spidermonkey.Runtime()

class DocTestPyParser(doctest.DocTestParser):

    _EXAMPLE_RE = re.compile(r'''
        # Source consists of a PS1 line followed by zero or more PS2 lines.
        (?P<source>
            (?:^(?P<indent> [ ]*) py>    .*)    # PS1 line
            (?:\n           [ ]*  \.\.\. .*)*)  # PS2 lines
        \n?
        # Want consists of any non-blank lines that do not start with PS1.
        (?P<want> (?:(?![ ]*$)    # Not a blank line
                     (?![ ]*py>)  # Not a line starting with PS1
                     .*$\n?       # But any other line
                  )*)
        ''', re.MULTILINE | re.VERBOSE)


class DocTestJSParser(doctest.DocTestParser):
    "Doctest parser that creates calls into JavaScript."

    _EXAMPLE_RE = re.compile(r'''
        # Source consists of a PS1 line followed by zero or more PS2 lines.
        (?P<source>
            (?:^(?P<indent> [ ]*) js>    .*)    # PS1 line
            (?:\n           [ ]*  \.\.\. .*)*)  # PS2 lines
        \n?
        # Want consists of any non-blank lines that do not start with PS1.
        (?P<want> (?:(?![ ]*$)    # Not a blank line
                     (?![ ]*js>)  # Not a line starting with PS1
                     .*$\n?       # But any other line
                  )*)
        ''', re.MULTILINE | re.VERBOSE)

    def parse(self, string, name='<string>'):
        r =doctest.DocTestParser.parse(self, string, name)
        for s in r:
            if isinstance(s, doctest.Example):
                s.source = "JS(%r)\n" % s.source
        return r

def setUp(test):
    zope.testing.setupstack.setUpDirectory(test)
    old_time = time.time
    zope.testing.setupstack.register(test, setattr, time, 'time', old_time)
    now = [1294777185.01]
    def time_time():
        now[0] += 0.1
        return now[0]
    time.time = time_time

    zope.testing.module.setUp(test)
    zope.testing.setupstack.register(test, zope.testing.module.tearDown, test)

    cx = run_time.new_context()
    test.globs['JS'] = JS = cx.execute
    cx.add_global('line2pc', 0)
    cx.add_global('djConfig', dict(baseUrl=baseUrl))

    def load(name):
        JS(open(name).read(), name)

    cx.add_global('load', load)

    load(baseUrl+'dojo.js.uncompressed.js')
    JS('console').log = lambda s: sys.stdout.write('%s\n' % (s, ))
    JS('console').error = lambda s: sys.stdout.write('Error: %s\n' % (s, ))


    load(os.path.join(os.path.dirname(__file__), 'test_setup.js'))
    test.globs['xhr_respond'] = JS('xhr_respond')
    JS('dojo.registerModulePath("zc.dozodb", "%s")' %
       os.path.join(os.path.dirname(__file__), 'dozodb')
       )

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            manuel.doctest.Manuel(parser=DocTestJSParser()) +
            manuel.doctest.Manuel(parser=DocTestPyParser()) +
            manuel.capture.Manuel(),
            'dozodb.test',
            setUp=setUp, tearDown=zope.testing.setupstack.tearDown),
        ))
