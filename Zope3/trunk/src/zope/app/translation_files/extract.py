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

This script extracts translatable strings and creates a single zope.pot file.

$Id: extract.py,v 1.2 2003/08/04 11:11:55 jim Exp $
"""

import os, sys, fnmatch
import pygettext


usage = """python extract.py [files]
"""

def app_dir():
    try:
        import zope.app
    except ImportError:
        # Couldn't import zope.app, need to add something to the Python
        # path

        # Get the path of the src
        translation_files = os.path.abspath(os.path.dirname(sys.argv[0]))
        app = os.path.dirname(translation_files)
        zope = os.path.dirname(app)
        src = os.path.dirname(zope)
        sys.path.insert(0, src)

        import zope.app

    dir = os.path.dirname(zope.app.__file__)

    return dir

def find_files(dir, pattern, exclude=()):


    files = []

    def visit(files, dirname, names):
        files += [os.path.join(dirname, name)
                  for name in fnmatch.filter(names, pattern)
                  if name not in exclude]
        
    os.path.walk(dir, visit, files)

    return files

def zcml_strings(dir, domain="zope"):
    from zope.app._app import config
    dirname = os.path.dirname
    site_zcml = os.path.join(dirname(dirname(dirname(dir))), "site.zcml")
    context = config(site_zcml, execute=False)
    return context.i18n_strings.get(domain, {})

def main(argv=sys.argv):
    dir = app_dir()

    strings = zcml_strings(dir)

    # OK, now what. I need someone who knows POT files.
    # Stephan, heeeeelp.
    print strings

    sys.argv[1:] = ['-ozope.pot',]+find_files(dir, '*.py',
                                            exclude=["pygettext.py"])
    pygettext.main()

    # We import zope.tal.talgettext here because we can't rely on the
    # right sys path until app_dir has run
    from zope.tal import talgettext

    sys.argv[1:] = ['-uzope.pot', '-ozope.pot',]+find_files(dir, '*.pt')
    talgettext.main()


if __name__ == '__main__':
    main()
