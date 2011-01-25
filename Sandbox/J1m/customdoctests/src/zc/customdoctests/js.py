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

parser = zc.customdoctests.DocTestParser(ps1='js>', handler_name='JS')

def setUp(test_or_self):
    globs = getattr(test_or_self, 'globs', test_or_self.__dict__)

    global run_time
    if run_time is None:
        run_time = spidermonkey.Runtime()

    cx = run_time.new_context()
    globs['JS'] = JS = cx.execute
    globs['add_js_global'] = cx.add_global


    # Emulate rhino load:
    def load(name):
        JS(open(name).read(), name)

    cx.add_global('load', load)         # rhino compat
    cx.add_global('print',
                  lambda s: sys.stdout.write('%s\n' % (s, ))) # rhino compat

    cx.add_global('console', dict(
        error = lambda s: sys.stdout.write('Error: %s\n' % (s, )),
        info = lambda s: sys.stdout.write('Info: %s\n' % (s, )),
        log = lambda s: sys.stdout.write('%s\n' % (s, )),
        ))
