##############################################################################
#
# Copyright (c) 2003 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

$Id$
"""
import unittest
import BTrees
import zope.event
import zope.component
from zope.app.testing import placelesssetup
from zope.configuration import xmlconfig
from zc.sharing import policy
import zc.sharing
import zc.sharing.sharing
import zope.app.security
import zope.annotation.interfaces
import zope.annotation.attribute
from zope.testing import module
import zope.security.management

def zcml(s):
    context = xmlconfig.file('meta.zcml', package=zope.app.security)
    context = xmlconfig.file('meta.zcml', context=context,
                             package=zc.sharing)
    xmlconfig.string(s, context)

def zcmlSetUp(test):
    placelesssetup.setUp()
    module.setUp(test, 'zc.sharing.zcml_text')
    test.globs['__old'] = policy.systemAdministrators

def zcmlTearDown(test):
    placelesssetup.tearDown()
    zc.sharing.sharing.clearPrivileges()
    module.tearDown(test, 'zc.sharing.zcml_text')
    policy.systemAdministrators = test.globs['__old']

def setUpSharing(test):
    placelesssetup.setUp()
    module.setUp(test, 'zc.sharing.SHARING')
    zope.component.provideAdapter(
        zope.annotation.attribute.AttributeAnnotations,
        [zope.annotation.interfaces.IAttributeAnnotatable],
        zope.annotation.interfaces.IAnnotations,
        )
    events = test.globs['events'] = []
    zope.event.subscribers.append(events.append)
    zope.security.management.endInteraction()

def tearDownSharing(test):
    placelesssetup.tearDown()
    module.tearDown(test, 'zc.sharing.SHARING')
    removed = zope.event.subscribers.pop()
    assert test.globs['events'] is removed.__self__
    del test.globs['events'] # just to be sure
    zc.sharing.sharing.clearPrivileges()

def tearDownIndex(test):
    placelesssetup.tearDown()
    zc.sharing.sharing.clearPrivileges()

def make_sure_sharing_uses_instance():
    """
    >>> import zope.interface
    >>> from zc.sharing import interfaces

    >>> class MyContent:
    ...     zope.interface.implements(interfaces.ISharable)

    >>> import zc.sharing.sharing
    >>> content = MyContent()
    >>> basesharing = zc.sharing.sharing.BaseSharing(content)
    >>> sharing = zc.sharing.sharing.Sharing(basesharing)
    
    >>> sharing.setBinaryPrivileges('bob', 21)

    >>> from zope.annotation.interfaces import IAnnotations
    >>> annotations = IAnnotations(content)
    >>> annotations[zc.sharing.sharing.key].__class__
    <class 'zc.sharing.sharing.SharingData'>
    
    """

def setUpPolicy(test):
    placelesssetup.setUp()
    test.globs['__old'] = policy.systemAdministrators

def tearDownPolicy(test):
    placelesssetup.tearDown()
    policy.systemAdministrators = test.globs['__old']
    zc.sharing.sharing.clearPrivileges()

def test_suite():
    from zope.testing import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'policy.txt',
            setUp=setUpPolicy, tearDown=tearDownPolicy),
        doctest.DocFileSuite(
            'zcml.txt', globs={'zcml': zcml},
            setUp=zcmlSetUp, tearDown=zcmlTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE,
            ),
        doctest.DocFileSuite(
            'sharing.txt',
            setUp=setUpSharing, tearDown=tearDownSharing,
            ),
        doctest.DocTestSuite(
            setUp=setUpSharing, tearDown=tearDownSharing,
            ),
        doctest.DocFileSuite(
            'index.txt',
            setUp=placelesssetup.setUp, tearDown=tearDownIndex,
            globs={'family': BTrees.family32},
            optionflags=doctest.INTERPRET_FOOTNOTES,
            ),
        doctest.DocFileSuite(
            'index.txt',
            setUp=placelesssetup.setUp, tearDown=tearDownIndex,
            globs={'family': BTrees.family64},
            optionflags=doctest.INTERPRET_FOOTNOTES,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

