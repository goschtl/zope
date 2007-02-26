##############################################################################
#
# Copyright (c) 2004-2005 Zope Corporation and Contributors.
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
"""Functional tests

$Id$
"""
import unittest
import transaction

from zope import copypastemove
from zope.interface import implements, Interface, directlyProvides
from zope.exceptions.interfaces import UserError

from zope.app.testing import ztapi
from zope.app.testing import functional
from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import Principal
from zope.app.authentication.principalfolder import IInternalPrincipal
from zope.app.authentication.testing import AppAuthenticationLayer

class FunkTest(functional.BrowserTestCase):

    def test_copypaste_duplicated_id_object(self):

        root = self.getRootFolder()

        # Create a principal Folder
        root['pf'] = PrincipalFolder()
        pf = root['pf']

        # Create a principal with p1 as login
        principal = Principal('p1')
        principal.login = 'p1'
        directlyProvides(principal, IInternalPrincipal)

        pf['p1'] = principal

        transaction.commit()
        self.assertEqual(len(pf.keys()), 1)
        #raise str([x for x in pf.keys()])

        response = self.publish('/pf/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'ids': [u'p1'],
                                      'container_copy_button': u'Copy'})
        self.assertEqual(response.getStatus(), 302)


        # Try to paste the file
        try:
            response = self.publish('/pf/@@contents.html',
                                    basic='mgr:mgrpw',
                                    form={'container_paste_button': ''})
        except UserError, e:
            self.assertEqual(
                str(e),
                "The given name(s) [u'p1'] is / are already being used")
        else:
            # test failed !
            self.asserEqual(1, 0)

    def test_cutpaste_duplicated_id_object(self):

        root = self.getRootFolder()

        # Create a principal Folder
        root['pf'] = PrincipalFolder()
        pf = root['pf']

        # Create a principal with p1 as login
        principal = Principal('p1')
        principal.login = 'p1'
        directlyProvides(principal, IInternalPrincipal)

        pf['p1'] = principal

        transaction.commit()
        self.assertEqual(len(pf.keys()), 1)
        #raise str([x for x in pf.keys()])

        response = self.publish('/pf/@@contents.html',
                                basic='mgr:mgrpw',
                                form={'ids': [u'p1'],
                                      'container_cut_button': u'Cut'})
        self.assertEqual(response.getStatus(), 302)


        # Try to paste the file
        try:
            response = self.publish('/pf/@@contents.html',
                                    basic='mgr:mgrpw',
                                    form={'container_paste_button': ''})
        except UserError, e:
            self.assertEqual(
                str(e),
                "The given name(s) [u'p1'] is / are already being used")
        else:
            # test failed !
            self.asserEqual(1, 0)


def test_suite():
    FunkTest.layer = AppAuthenticationLayer
    principalfolder = functional.FunctionalDocFileSuite('principalfolder.txt')
    principalfolder.layer = AppAuthenticationLayer
    groupfolder = functional.FunctionalDocFileSuite('groupfolder.txt')
    groupfolder.layer = AppAuthenticationLayer
    pau_prefix_and_searching = functional.FunctionalDocFileSuite(
        'pau_prefix_and_searching.txt')
    pau_prefix_and_searching.layer = AppAuthenticationLayer
    group_searching_with_empty_string = functional.FunctionalDocFileSuite(
        'group_searching_with_empty_string.txt')
    group_searching_with_empty_string.layer = AppAuthenticationLayer
    special_groups = functional.FunctionalDocFileSuite('special-groups.txt')
    special_groups.layer = AppAuthenticationLayer
    issue663 = functional.FunctionalDocFileSuite('issue663.txt')
    issue663.layer = AppAuthenticationLayer
    return unittest.TestSuite((
        principalfolder,
        groupfolder,
        pau_prefix_and_searching,
        group_searching_with_empty_string,
        special_groups,
        unittest.makeSuite(FunkTest),
        issue663,
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
