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
"""Message id extraction script

This script extracts translatable strings and creates a single wiki.pot file.

$Id: extract.py,v 1.1 2003/12/16 10:05:54 nmurthy Exp $
"""

import os, sys, fnmatch
from zope.tal import talgettext
from zope.app.translation_files import pygettext


usage = """python extract.py [files]
"""

def wiki_dir():
    import zope.products.zwiki
    return os.path.dirname(zope.products.zwiki.__file__)


def find_files(dir, pattern, exclude=()):
    files = []
    def visit(files, dirname, names):
        files += [os.path.join(dirname, name)
                  for name in fnmatch.filter(names, pattern)
                  if name not in exclude]
        
    os.path.walk(dir, visit, files)

    return files


def main(argv=sys.argv):
    dir = wiki_dir()
    sys.argv[1:] = ['-owiki.pot',]+find_files(dir, '*.py',
                                              exclude=["pygettext.py"])
    pygettext.main()
    sys.argv[1:] = ['-uwiki.pot', '-owiki.pot',]+find_files(dir, '*.pt')
    talgettext.main()


if __name__ == '__main__':
    main()
