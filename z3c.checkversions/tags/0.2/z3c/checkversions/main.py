##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
"""This script will check new package versions of either
your current installed distributions or a buildout file if provided.
It can detect major or minor versions availability:
level 0 gets the highest version (X.y.z),
level 1 gets the highest intermediate version (x.Y.z),
level 2 gets the highest minor version (x.y.Z).

Using level 2, you can automatically retrieve all bugfix versions of a buildout.
"""

from optparse import OptionParser

def main():

    parser = OptionParser(description=__doc__)

    parser.add_option('-l', '--level',
                      type='int',
                      dest='level',
                      default=0,
                      help=u"Version level to check")

    parser.add_option('-i', '--index',
                      dest='index',
                      help=u"Alternative package index URL")

    parser.add_option('-v', '--verbose',
                      dest='verbose',
                      action='store_true',
                      default=False,
                      help=u"Verbose mode (prints old versions too)")
    options, args = parser.parse_args()

    if len(args) > 1:
        parser.error("You must specify only one argument")

    buildoutcfg = False
    if len(args) == 1:
        buildoutcfg = args[0]

    kw = {}
    if options.index is not None:
        kw['index_url'] = options.index

    if buildoutcfg:
        import buildout
        checker = buildout.Checker(filename=buildoutcfg,
                                   verbose=options.verbose,
                                   **kw)
    else:
        import installed
        checker = installed.Checker(verbose=options.verbose)

    checker.check(level=options.level)


if __name__ == '__main__':
    main()

