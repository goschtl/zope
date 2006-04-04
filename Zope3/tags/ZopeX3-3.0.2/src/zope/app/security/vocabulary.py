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
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.app.security.interfaces import IPermission


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
