"""SiteErrorLog tests

Note: Tests require Zope >= 2.7

$Id: testVirtualHostMonster.py 24763 2004-05-17 05:59:28Z philikon $
"""

from Testing.makerequest import makerequest

import Zope
Zope.startup()

import sys
import unittest


class SiteErrorLogTests(unittest.TestCase):

    def setUp(self):
        get_transaction().begin()
        self.app = makerequest(Zope.app())
        try:
            self.app.manage_addDTMLMethod('doc', '')
        except:
            self.tearDown()

    def tearDown(self):
        get_transaction().abort()
        self.app._p_jar.close()

    def testInstantiation(self):
        # Retrieve the error_log by ID
        sel_ob = getattr(self.app, 'error_log', None)

        # Does the error log exist?
        self.assert_(sel_ob is not None)

        # Is the __error_log__ hook in place?
        self.assert_(self.app.__error_log__ == sel_ob)

        # Right now there should not be any entries in the log
        self.assertEquals(len(sel_ob.getLogEntries()), 0)

    def testSimpleException(self):
        # Grab the Site Error Log and make sure it's empty
        sel_ob = self.app.error_log
        previous_log_length = len(sel_ob.getLogEntries())

        # Fill the DTML method at self.root.doc with bogus code
        dmeth = self.app.doc
        dmeth.manage_upload(file="""<dtml-var expr="1/0">""")

        # "Faking out" the automatic involvement of the Site Error Log
        # by manually calling the method "raising" that gets invoked
        # automatically in a normal web request environment.
        try:
            dmeth.__call__()
        except ZeroDivisionError:
            sel_ob.raising(sys.exc_info())

        # Now look at the SiteErrorLog, it has one more log entry
        self.assertEquals(len(sel_ob.getLogEntries()), previous_log_length+1)

    def testIgnoredException(self):
        # Grab the Site Error Log
        sel_ob = self.app.error_log
        previous_log_length = len(sel_ob.getLogEntries())

        # Tell the SiteErrorLog to ignore ZeroDivisionErrors
        current_props = sel_ob.getProperties()
        ignored = list(current_props['ignored_exceptions'])
        ignored.append('ZeroDivisionError')
        sel_ob.setProperties( current_props['keep_entries']
                            , copy_to_zlog = current_props['copy_to_zlog']
                            , ignored_exceptions = ignored
                            )

        # Fill the DTML method at self.root.doc with bogus code
        dmeth = self.app.doc
        dmeth.manage_upload(file="""<dtml-var expr="1/0">""")

        # "Faking out" the automatic involvement of the Site Error Log
        # by manually calling the method "raising" that gets invoked
        # automatically in a normal web request environment.
        try:
            dmeth.__call__()
        except ZeroDivisionError:
            sel_ob.raising(sys.exc_info())

        # Now look at the SiteErrorLog, it must have the same number of 
        # log entries
        self.assertEquals(len(sel_ob.getLogEntries()), previous_log_length)

    def testCleanup(self):
        # Need to make sure that the __error_log__ hook gets cleaned up
        self.app._delObject('error_log')
        self.assertEquals(getattr(self.app, '__error_log__', None), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SiteErrorLogTests))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

