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
"""Component Architecture Tests

$Id$
"""

import os
import shutil
import sys
import tempfile
import unittest
import warnings
from zope.testing import doctest
import zope.deprecation

# Used in doctests
from deprecation import deprecated
demo1 = 1
deprecated('demo1', 'demo1 is no more.')

demo2 = 2
deprecated('demo2', 'demo2 is no more.')

demo3 = 3
deprecated('demo3', 'demo3 is no more.')

demo4 = 4
def deprecatedemo4():
    """Demonstrate that deprecate() also works in a local scope."""
    deprecated('demo4', 'demo4 is no more.')

def warn(message, type_, stacklevel):
    print "From tests.py's showwarning():"
    
    frame = sys._getframe(stacklevel)
    path = frame.f_globals['__file__']
    file = open(path)
    lineno = frame.f_lineno
    for i in range(lineno):
        line = file.readline()

    print "%s:%s: %s: %s\n  %s" % (
        path,
        frame.f_lineno,
        type_.__name__,
        message,
        line.strip(),
        )


def setUpCreateModule(test):
    d = test.globs['tmp_d'] = tempfile.mkdtemp('deprecation')

    def create_module(**modules):
        for name, src in modules.iteritems():
            f = open(os.path.join(d, name+'.py'), 'w')
            f.write(src)
            f.close()
            test.globs['created_modules'].append(name)

    test.globs['created_modules'] = []
    test.globs['create_module'] = create_module

    zope.deprecation.__path__.append(d)

def tearDownCreateModule(test):
    zope.deprecation.__path__.pop()
    shutil.rmtree(test.globs['tmp_d'])
    for name in test.globs['created_modules']:
        sys.modules.pop(name, None)

def setUp(test):
    test.globs['saved_warn'] = warnings.warn
    warnings.warn = warn
    setUpCreateModule(test)

def tearDown(test):
    tearDownCreateModule(test)
    warnings.warn = test.globs['saved_warn']
    del object.__getattribute__(sys.modules['zope.deprecation.tests'],
                                '_DeprecationProxy__deprecated')['demo4']

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=tearDown,
                             optionflags=doctest.ELLIPSIS),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
