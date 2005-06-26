##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Test the Localizer language integration for CPS

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_suite():
    from Testing.ZopeTestCase import installProduct, FunctionalDocFileSuite
    installProduct('Five')
    installProduct('BTreeFolder2')
    installProduct('CMFCalendar')
    installProduct('CMFCore')
    installProduct('CMFDefault')
    installProduct('CMFTopic')
    installProduct('DCWorkflow')
    installProduct('Localizer')
    installProduct('MailHost')
    installProduct('CPSCore')
    installProduct('CPSDefault')
    installProduct('CPSDirectory')
    installProduct('CPSUserFolder')
    installProduct('TranslationService')
    installProduct('SiteAccess')
    # XXX: these products should (and used to be) be optional, but they aren't
    # right now.
    installProduct('CPSForum')
    installProduct('CPSSubscriptions')
    installProduct('CPSNewsLetters')
    installProduct('CPSSchemas')
    installProduct('CPSDocument')
    installProduct('PortalTransforms')
    installProduct('Epoz')

    # Optional products
    try: installProduct('NuxMetaDirectories')
    except: pass
    try: installProduct('CPSRSS')
    except: pass
    try: installProduct('CPSChat')
    except: pass
    try: installProduct('CPSCalendar')
    except: pass
    try: installProduct('CPSCollector')
    except: pass
    try: installProduct('CPSMailBoxer')
    except: pass

    return FunctionalDocFileSuite('cps_test_localizer.txt',
                                  package='Products.Five.browser.tests')

if __name__ == '__main__':
    framework()
