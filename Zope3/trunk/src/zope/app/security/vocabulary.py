##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Permission Id Vocabulary.

This vocabulary provides permission IDs.

$Id: $
"""
from zope.security.checker import CheckerPublic
from zope.app import zapi
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.schema.interfaces import ISource, ISourceQueriables
from zope.app.security.interfaces import IPermission
from zope.app.component.localservice import queryNextService

class PermissionIdsVocabulary(SimpleVocabulary):
    """A vocabular of permission IDs.
    
    Term values are the permission ID strings except for 'zope.Public', which
    is the global permission CheckerPublic.
    
    Term titles are the permission ID strings except for 'zope.Public', which
    is shortened to 'Public'.
    
    Terms are sorted by title except for 'Public', which always appears as
    the first term.

    To illustrate, we need to register the permission IDs vocab:

        >>> from zope.app.tests.placelesssetup import setUp, tearDown
        >>> setUp()
        >>> from zope.schema.vocabulary import getVocabularyRegistry
        >>> registry = getVocabularyRegistry()
        >>> registry.register('Permission Ids', PermissionIdsVocabulary)

    We also need to register some sample permission utilities, including
    the special permission 'zope.Public':
    
        >>> from zope.app.security.interfaces import IPermission
        >>> from zope.app.security.permission import Permission
        >>> from zope.app.tests import ztapi
        >>> ztapi.provideUtility(IPermission, Permission('zope.Public'),
        ...     'zope.Public')
        >>> ztapi.provideUtility(IPermission, Permission('b'), 'b')
        >>> ztapi.provideUtility(IPermission, Permission('a'), 'a')

    We can now lookup these permissions using the vocabulary:
    
        >>> vocab = registry.get(None, 'Permission Ids')

	The non-public permissions 'a' and 'b' are string values:
	
	    >>> vocab.getTermByToken('a').value
	    u'a'
	    >>> vocab.getTermByToken('b').value
	    u'b'

    However, the public permission value is CheckerPublic:
    
        >>> vocab.getTermByToken('zope.Public').value is CheckerPublic
        True

    and its title is shortened:

        >>> vocab.getTermByToken('zope.Public').title
        u'Public'

    The terms are sorted by title except for the public permission, which is
    listed first:
    
        >>> [term.title for term in vocab]
        [u'Public', u'a', u'b']
        
        >>> tearDown()
    """
    def __init__(self, context):
        terms = []
        permissions = zapi.getUtilitiesFor(IPermission, context)
        for name, permission in permissions:
            if name == 'zope.Public':
                terms.append(SimpleTerm(
                    CheckerPublic, 'zope.Public', u'Public'))
            else:
                terms.append(SimpleTerm(name, name, name))
        terms.sort(lambda lhs, rhs: \
            lhs.title == u'Public' and -1 or cmp(lhs.title, rhs.title))
        super(PermissionIdsVocabulary, self).__init__(terms)


class PrincipalSource(object):
    """Generic Principal Source"""
    implements(ISource, ISourceQueriables)

    def __contains__(self, id):
        """Test for the existence of a user.

        We want to check whether the system knows about a particular
        principal, which is referenced via its id. The source will go through
        the most local authentication service to look for the
        principal. Whether the service consults other services to give an
        answer is up to the service itself.

        First we need to create a dummy service that will return a user, if
        the id is 'bob'.
        
        >>> class DummyService:
        ...     def getPrincipal(self, id):
        ...         if id == 'bob':
        ...             return id

        Since we do not want to bring up the entire component architecture, we
        simply monkey patch the `getService()` method to always return our
        dummy authentication service.

        >>> temp = zapi.getService
        >>> zapi.getService = lambda name: DummyService()

        Now initialize the principal source and test the method

        >>> source = PrincipalSource()
        >>> 'jim' in source
        False
        >>> 'bob' in source
        True

        Now revert our patch.

        >>> zapi.getService = temp
        """
        auth = zapi.getService(zapi.servicenames.Authentication)
        principal = auth.getPrincipal(id)
        return principal is not None

    def getQueriables(self):
        """Returns an iteratable of queriables. 

        Queriables are responsible for providing interfaces to search for
        principals by a set of given parameters (can be different for the
        various queriables). This method will walk up through all of the
        authentication services to look for queriables.

        >>> class DummyService1:
        ...     __parent__ = None
        ...     def __repr__(self): return 'dummy1'
        >>> dummy1 = DummyService1()
        
        >>> class DummyService2:
        ...     implements(ISourceQueriables)
        ...     __parent__ = None
        ...     def getQueriables(self):
        ...         return 1, 2, 3
        >>> dummy2 = DummyService2()
        
        >>> from zope.app.component.localservice import testingNextService
        >>> testingNextService(dummy1, dummy2, 'Authentication')
        
        >>> temp = zapi.getService
        >>> zapi.getService = lambda name: dummy1

        >>> source = PrincipalSource()
        >>> list(source.getQueriables())
        [dummy1, 1, 2, 3]

        >>> zapi.getService = temp
        """
        auth = zapi.getService(zapi.servicenames.Authentication)
        while True:
            queriables = ISourceQueriables(auth, None)
            if queriables is None:
                yield auth
            else:
                for queriable in queriables.getQueriables():
                    yield queriable
            auth = queryNextService(auth, zapi.servicenames.Authentication)
            if auth is None:
                break
