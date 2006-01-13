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
"""Test the if header handling code

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
import urllib

from zope.interface import Interface
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest
from zope.security.testing import Principal, Participation
from zope.security.management import newInteraction, endInteraction, \
     queryInteraction

from zope.app.testing import ztapi
from zope.app.container.interfaces import IReadContainer
from zope.app.file.file import File
from zope.app.locking.interfaces import ILockable, ILockStorage, ILockTracker
from zope.app.locking.adapter import LockingAdapterFactory, LockingPathAdapter
from zope.app.locking.storage import PersistentLockStorage
from zope.app.keyreference.interfaces import IKeyReference
from zope.app.traversing.interfaces import IPathAdapter
from zope.app.traversing.browser import AbsoluteURL, SiteAbsoluteURL
from zope.app.traversing.browser.interfaces import IAbsoluteURL

from zope.app.dav.common import MultiStatus, MultiStatusResponse, \
     IMultiStatusResponse
from zope.app.dav.interfaces import IIfHeader
from zope.app.dav.ifhandler import IfParser


class FakeAbsoluteURL(object):
    # If the context is a folder return '/folder' else return '/file'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        context = self.context
        request = self.request

        if IReadContainer.providedBy(context):
            return '/folder'
        return '/file'

    __call__ = __str__

    def breadcrumbs(self):
        if IReadContainer.providedBy(context):
            name = 'folder'
        else:
            name = 'file'

        return ({'name': name,
                 'url': 'http://localhost:8080/%s' % name,
                 },
                )


class FakeKeyReference(object):
    """Fake keyref for testing"""
    def __init__(self, object):
        self.object = object

    def __call__(self):
        return self.object

    def __hash__(self):
        return id(self.object)

    def __cmp__(self, other):
        return cmp(id(self.object), id(other.object))


class TestIfParser(unittest.TestCase):

    def setUp(self):
        super(TestIfParser, self).setUp()
        
        ztapi.provideAdapter(Interface, IKeyReference, FakeKeyReference)
        ztapi.provideAdapter(Interface, ILockable, LockingAdapterFactory)
        ztapi.provideAdapter(None, IPathAdapter, LockingPathAdapter,
                             "locking")

        self.storage = storage = PersistentLockStorage()
        ztapi.provideUtility(ILockStorage, storage)
        ztapi.provideUtility(ILockTracker, storage)

        ztapi.browserView(None, 'absolute_url', FakeAbsoluteURL)
        ztapi.browserView(None, '', FakeAbsoluteURL, providing = IAbsoluteURL)

        self.token = 'opaquelocktoken:somelocktoken'

    def tearDown(self):
        super(TestIfParser, self).tearDown()

        # I do a lot of locking - make sure that I remember to end the
        # current interaction
        if queryInteraction() is not None:
            endInteraction()

        del self.storage

    def _lockcontent(self, content, locktoken = None):
        # simply lock content with locktoken if set and return the lockinfo
        participation = Participation(Principal('michael'))
        newInteraction(participation)
        lockable = ILockable(content)
        lockable.lock()
        lockinfo = lockable.getLockInfo()
        if locktoken is not None:
            lockinfo['lockuri'] = locktoken
        return lockinfo

    def test_basic(self):
        request = TestRequest()
        context = File('some content', 'text/plain')
        ifparser = IfParser(context, request)
        self.assert_(verifyObject(IIfHeader, ifparser))
        # not locked -> true
        self.assertEqual(ifparser(), True)
        request = TestRequest(**{'IF': '(<some lock token>)'})
        ifparser = IfParser(context, request)
        # context not locked -> true
        self.assertEqual(ifparser(), True)

    def test_on_locked_file_no_header(self):
        request = TestRequest()
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context)
        ifparser = IfParser(context, request)
        self.assertEqual(ifparser(), False)

    def test_on_locked_file_no_token(self):
        request = TestRequest(**{'IF': '(<%s>)' % self.token})
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context)
        ifparser = IfParser(context, request)
        # lock tokens don't match since it is empty so this should fail.
        self.assertEqual(ifparser(), False)

    def test_on_locked_file_with_token(self):
        request = TestRequest(**{'IF': '(<%s>)' % self.token})
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context, self.token)
        ifparser = IfParser(context, request)
        # tokens match so this is true
        self.assertEqual(ifparser(), True)

    def test_resource_correct(self):
        request = TestRequest(**{
            'IF': '<http://localhost:8080/file> (<%s>)' % self.token,
            })
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context, self.token)
        ifparser = IfParser(context, request)
        # resource and token match
        self.assertEqual(ifparser(), True)

    def test_resource_empty_token(self):
        # test correct resource with wrong token
        request = TestRequest(**{
            'IF': '<http://localhost:8080/file> (<%s>)' % self.token,
            })
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context)
        ifparser = IfParser(context, request)
        # resrouce matches but the token doesn't
        self.assertEqual(ifparser(), False)

    def test_wrong_resource_empty_token(self):
        request = TestRequest(**{
            'IF': '<http://localhost:8080/folder/> (<%s>)' % self.token,
            })
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context, self.token)
        ifparser = IfParser(context, request)
        # resource don't match but either does the tokens -> True ???
        self.assertEqual(ifparser(), True)

    def test_resource_wrong_wrong_token(self):
        request = TestRequest(**{
            'IF': '<http://localhost:8080/folder/> (<%s>)' % self.token,
            })
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context, self.token)
        ifparser = IfParser(context, request)
        # resources don't match so this passes since 
        self.assertEqual(ifparser(), True)

    def test_multiple_resources_correct_token(self):
        request = TestRequest(**{
            'IF': """<http://localhost:8080/folder/> (<dummylock:token>)"""
                  """<http://localhost:8080/file> (<%s>)"""
            %(self.token),
            })
        context = File('some content', 'text/plain')
        lockinfo = self._lockcontent(context, self.token)
        ifparser = IfParser(context, request)
        # one of the resources and tokens match -> good
        self.assertEqual(ifparser(), True)


class TestMultiStatus(unittest.TestCase):

    def test_no_properties(self):
        ms = MultiStatus()
        asstr = ms.body.toxml('utf-8')
        self.assertEqual(asstr, '<?xml version="1.0" encoding="utf-8"?>\n<multistatus xmlns="DAV:"/>')

##     def test_one_resource_no_props(self):
##         ms = MultiStatus()
##         context = File('some content', 'text/plain')
##         request = TestRequest()
##         msr = ms.addResponse(context, request)
##         self.assert_(verifyObject(IMultiStatusResponse, msr))

##         asstr = ms.body.toxml('utf-8')
##         self.assertEqual(asstr, '<?xml version="1.0" encoding="utf-8"?>\n<multistatus xmlns="DAV:"><response><href>/file</href><status>200 OK</status></response></multistatus>')

    def test_one_resource_one_none_prop(self):
        ms = MultiStatus()
        context = File('some content', 'text/plain')
        request = TestRequest()
        msr = ms.addResponse(context, request)

        self.assertRaises(TypeError, msr.addPropertyByStatus,
                          ('DAV:', None, None, 200))

##     def test_one_resource_one_prop(self):
##         ms = MultiStatus()
##         context = File('some content', 'text/plain')
##         request = TestRequest()
##         msr = ms.addResponse(context, request)

##         msr = ms.addResponse(context, request)
##         el = ms.body.createElementNS('DAV:', 'foo')
##         el.appendChild(ms.body.createTextNode('foo content'))
##         msr.addPropertyByStatus('DAV', None, el, 200)
##         self.assertEqual(ms.body.toxml('utf-8'), '')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestIfParser),
        unittest.makeSuite(TestMultiStatus),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
