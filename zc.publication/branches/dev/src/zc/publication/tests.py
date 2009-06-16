##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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

from zope.testing import doctest, setupstack
import manuel
import manuel.doctest
import manuel.testing
import os
import paste.deploy
import re
import textwrap
import unittest
import webtest

def assignment_manuel():
    assignment_re = re.compile(
        r"[^\n]*::(?P<value>(\n| [^\n]*\n)+?)"
        " *\.\. -> (?P<name>\w+)(?P<strip> +strip)? *\n")

    m = manuel.Manuel()

    @m.parser
    def parse(document):
        for region in document.find_regions(assignment_re):
            data = region.start_match.groupdict()
            data['value'] = textwrap.dedent(data['value'].expandtabs())
            if data.get('strip'):
                data['value'] = data['value'].strip()
            source = "%(name)s = %(value)r\n" % data
            example = doctest.Example(source, '', lineno=region.lineno-1)
            document.replace_region(region, example)

    m2 = manuel.doctest.Manuel()
    m2.extend(m)

    return m2

def testapp(name, *args, **kw):
    name = os.path.abspath(name)
    app = paste.deploy.loadapp('config://'+name)
    return webtest.TestApp(app, *args, **kw)

def setUp(test):
    setupstack.setUpDirectory(test)
    test.globs['testapp'] = testapp

def test_suite():
    return unittest.TestSuite((
        manuel.testing.TestSuite(
            assignment_manuel(),
            'README.txt',
            setUp=setUp, tearDown=setupstack.tearDown),
        ))

