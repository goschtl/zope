#! /usr/bin/env python
import unittest
import sys

#                  PackageName     Required?
CMF_PACKAGES = [ ( 'CMFCore',       1 )
               , ( 'CMFDefault',    1 )
               , ( 'CMFTopic',      1 )
               , ( 'CMFCalendar',   0 )
               , ( 'DCWorkflow',    0 )
               ]

PACKAGES_UNDER_TEST = []

def test_suite():

    import Zope

    try:
        Zope.startup()
    except AttributeError:  # Zope <= 2.6.0
        pass

    from Products.CMFCore.tests.base.utils import build_test_suite

    suite = unittest.TestSuite()

    packages = PACKAGES_UNDER_TEST or CMF_PACKAGES

    for package_name, required in packages:
        dotted = 'Products.%s.tests' % package_name
        suite.addTest( build_test_suite( dotted
                                       , [ 'test_all' ]
                                       , required=required
                                       ) )

    return suite

def usage():

    USAGE = """\
all_cmf_tests.py [-?] <package_name>*

where

  package_name is the list of packages to be tested
  default: %s
"""

    print USAGE % CMF_PACKAGES
    sys.exit( 2 )

def main():

    import getopt

    try:
        opts, args = getopt.getopt( sys.argv[1:], 'v?' )
    except getopt.GetoptError:
        usage()

    sys.argv[ 1: ] = []
    PASSTHROUGH = ( '-v', )

    for k, v in opts:

        if k in PASSTHROUGH:
            sys.argv.append( k )

        if k == '-?' or k == '--help':
            usage()

    for arg in args:
        PACKAGES_UNDER_TEST.append( ( arg, 1 ) )

    unittest.main(defaultTest='test_suite')

if __name__ == '__main__':

    main()
