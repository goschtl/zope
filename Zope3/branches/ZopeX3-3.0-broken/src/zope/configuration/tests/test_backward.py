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
"""Test backward-compatiblity.

$Id$
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.configuration import config, xmlconfig
from zope.configuration.tests.test_xmlconfig import clean_text_w_paths

def test_directive_and_integration():
    r"""

    To see if the backward compatability meta configurations are
    working, well evaluate a test zcml file and see if we get the
    expected actions:

    >>> from zope.configuration import tests
    >>> context = xmlconfig.file("backward.zcml", tests, execute=False)
    >>> for action in context.actions:
    ...   print action[:2]
    ...   print action[2]
    ...   print clean_text_w_paths(unicode(action[5]))
    ...   if action[5].text.strip():
    ...      print action[5].text.strip()
    (('simple', u'aa', u'xxx', u'cc'), f)
    (u'aa', u'xxx', u'cc')
    File "tests/backward.zcml", line 26.2-26.34
        <test:simple a="aa" c="cc">first</test:simple>
    first
    (('newsimple', u'naa', u'nbb', u'ncc'), f)
    (u'naa', u'nbb', u'ncc')
    File "tests/backward.zcml", line 27.2-27.48
        <test:newsimple a="naa" c="ncc" b="nbb">second</test:newsimple>
    second
    ('Complex.__init__', None)
    ()
    File "tests/backward.zcml", line 48.2-53.2
        <test:testc a="ca" c="cc">
           Third
           <test:factory factory=".f">
              Fourth
           </test:factory>
        </test:testc>
    Third
    (('Complex.factory', 1, 2), u'.f')
    (u'ca',)
    File "tests/backward.zcml", line 50.5-52.5
           <test:factory factory=".f">
              Fourth
           </test:factory>
    Fourth
    (('Complex', 1, 2), f)
    (u'xxx', u'cc')
    File "tests/backward.zcml", line 48.2-53.2
        <test:testc a="ca" c="cc">
           Third
           <test:factory factory=".f">
              Fourth
           </test:factory>
        </test:testc>
    Third

    """

def test_directive_and_integration_w_python_keywords():
    r"""

    >>> from zope.configuration import tests
    >>> context = xmlconfig.file("backwardkw.zcml", tests, execute=False)
    >>> for action in context.actions:
    ...   print action[:2]
    ...   print action[2]
    ...   print clean_text_w_paths(unicode(action[5]))
    ...   print action[5].text.strip()
    (('k', u'f'), f)
    (u'f', u'c', u'x')
    File "tests/backwardkw.zcml", line 26.2-26.43
        <test:k  for="f"  class="c"  x="x" >first</test:k>
    first
    (('k', u'ff'), f)
    (u'ff', u'cc', u'xx')
    File "tests/backwardkw.zcml", line 27.2-27.44
        <test:k2 for="ff" class="cc" x="xx">second</test:k2>
    second
    
    """

def test_directive_and_integration_w_extra_arguments():
    r"""

    >>> from zope.configuration import tests
    >>> context = xmlconfig.file("backwardkwextra.zcml", tests, execute=False)
    >>> for action in context.actions:
    ...   print action[:2]
    ...   print action[2]
    ...   print clean_text_w_paths(unicode(action[5]))
    (('k', u'f'), f)
    (u'f', u'c', u'x', {'a': u'a', 'b': u'b'})
    File "tests/backwardkwextra.zcml", line 14.2-14.51
        <test:k  for="f"  class="c"  x="x" a="a" b="b" />
    """

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.configuration.backward'),
        DocTestSuite(),
        ))

if __name__ == '__main__': unittest.main()
