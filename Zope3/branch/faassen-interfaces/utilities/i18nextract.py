#!/usr/bin/env python2.3
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
"""Program to extract internationalization markup from Python Code,
Page Templates and ZCML.

This tool will extract all findable message strings from all
internationalizable files in your Zope 3 product. It only extracts
message ids of the specified domain. It defaults to the 'zope' domain
and the zope package.

Note: The Python Code extraction tool does not support domain
      registration, so that all message strings are returned for
      Python code.

Note: The script expects to be executed either from inside the Zope 3 source tree
      or with the Zope 3 source tree on the Python path.
      Execution from a symlinked directory inside the Zope 3 source tree will not work.

Usage: i18nextract.py [options]
Options:
    -h / --help
        Print this message and exit.
    -d / --domain <domain>
        Specifies the domain that is supposed to be extracted (i.e. 'zope')
    -p / --path <path>
        Specifies the package that is supposed to be searched
        (i.e. 'zope/app')
    -o dir
        Specifies a directory, relative to the package in which to put the
        output translation template.

$Id: i18nextract.py,v 1.6 2004/04/21 10:02:14 eckart Exp $
"""

import os, sys, getopt

def usage(code, msg=''):
    # Python 2.1 required
    print >> sys.stderr, __doc__
    if msg:
        print >> sys.stderr, msg
    sys.exit(code)

def app_dir():
    try:
        import zope
    except ImportError:
        # Couldn't import zope, need to add something to the Python path

        # Get the path of the src
        path = os.path.abspath(os.getcwd())
        while not path.endswith('src'):
            parentdir = os.path.dirname(path)
            if path == parentdir:
                # root directory reached
                break
            path = parentdir
        sys.path.insert(0, path)

        try:
            import zope
        except ImportError:
            usage(1, "Make sure the script has been executed "
                     "inside Zope 3 source tree.")

    return os.path.dirname(zope.__file__)

def main(argv=sys.argv):
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hd:p:o:',
            ['help', 'domain=', 'path=', 'python-only'])
    except getopt.error, msg:
        usage(1, msg)

    domain = 'zope'
    path = app_dir()
    include_default_domain = True
    output_dir = None
    python_only = None
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        elif opt in ('-d', '--domain'):
            domain = arg
            include_default_domain = False
        elif opt in ('-o', ):
            output_dir = arg
        elif opt in ('--python-only',):
            python_only = True
        elif opt in ('-p', '--path'):
            if not os.path.exists(arg):
                usage(1, 'The specified path does not exist.')
            path = arg
            # We might not have an absolute path passed in.
            if not path == os.path.abspath(path):
                cwd = os.getcwd()
                # This is for symlinks. Thanks to Fred for this trick.
                if os.environ.has_key('PWD'):
                    cwd = os.environ['PWD']
                path = os.path.normpath(os.path.join(cwd, arg))

    # When generating the comments, we will not need the base directory info,
    # since it is specific to everyone's installation
    src_start = path.rfind('src')
    base_dir = path[:src_start]

    output_file = domain+'.pot'
    if output_dir:
        output_dir = os.path.join(path, output_dir)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, output_file)

    print "base path: %r\nsearch path: %r\ndomain: %r\noutput file: %r" \
        % (base_dir, path, domain, output_file)

    from zope.app.translation_files.extract import POTMaker, \
         py_strings, tal_strings, zcml_strings

    maker = POTMaker(output_file, path)
    maker.add(py_strings(path, domain), base_dir)
    if not python_only:
        maker.add(zcml_strings(path, domain), base_dir)
        maker.add(tal_strings(path, domain, include_default_domain), base_dir)
    maker.write()

if __name__ == '__main__':
    main()
