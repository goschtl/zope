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
import re
import spidermonkey
import sys
import zc.customdoctests

run_time = None

def transform(s):
    if s[-1] == '\n':
        return (r'JS(r"""%s"""+"\n")' % s) + '\n'
    else:
        return r'JS(r"""%s""")' % s

parser = zc.customdoctests.DocTestParser(
    ps1='js>', comment_prefix='//', transform=transform)

# parser_ is like parser, except adds: var _ = to
# the fron of the executed code.
eq_parser = zc.customdoctests.DocTestParser(
    ps1='js!', comment_prefix='//',
    transform=lambda s: transform('var _ = ' + s))

def setUp(test_or_self):
    globs = getattr(test_or_self, 'globs', test_or_self.__dict__)

    global run_time
    if run_time is None:
        run_time = spidermonkey.Runtime()

    cx = run_time.new_context()
    globs['JS'] = JS = cx.execute
    globs['add_js_global'] = cx.add_global

    # Rhino & spidermonkey/js compatability functions
    cx.add_global('load', lambda name: JS(open(name).read(), name))
    cx.add_global('print',
                  lambda *s: sys.stdout.write('%s\n' % ' '.join(map(str, s)))
                  )
