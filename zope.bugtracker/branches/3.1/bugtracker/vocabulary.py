##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Vocabularies for the Bug Tracker

$Id: vocabulary.py,v 1.7 2004/03/18 18:04:54 philikon Exp $
"""
from persistent import Persistent
from persistent.dict import PersistentDict

from zope.interface import implements
from zope.schema.interfaces import ITokenizedTerm, ITitledTokenizedTerm
from zope.schema.interfaces import IVocabulary, IVocabularyTokenized
from zope.schema.vocabulary import getVocabularyRegistry
from zope.security.proxy import removeSecurityProxy 

from zope.app import zapi
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations

from bugtracker.interfaces import IManagableVocabulary, IBugTracker
from bugtracker.interfaces import IStatusVocabulary
from bugtracker.interfaces import IReleaseVocabulary
from bugtracker.interfaces import IPriorityVocabulary 
from bugtracker.interfaces import IBugTypeVocabulary
from bugtracker import TrackerMessageID as _


class SimpleTerm(Persistent):
    """A persistent vocabulary term.""" 
    implements(ITitledTokenizedTerm)

    def __init__(self, value, title):
        self.value = value
        self.title = title

    def getToken(self):
        return self.value

    token = property(getToken)
    

class ManagableVocabulary(object):
    """A vocabulary that stores its terms on an object.

    The terms of the vocabulary are persistent, so that they can be stored on
    the object in the ZODB. Annotations are used to store the terms.
    """
    implements(IManagableVocabulary)
    __used_for__ = IAnnotatable

    key = None

    interface = None

    def __init__(self, context):
        context = self._getRealContext(context)
        # When we use this vocabulary as an adapter, we always get an
        # unproxied context, but when it is used as a vocabulary, we usually
        # get proxied context, in which case we need to unwrap it.
        pureContext = removeSecurityProxy(context)
        self.annotations = IAnnotations(pureContext)
        if not self.annotations.get(self.key):
            self.annotations[self.key] = PersistentDict()
            self.annotations[self.key+'/default'] = None
    
    def __contains__(self, value):
        return value in self.annotations[self.key].keys()
    
    def __iter__(self):
        return iter(self.annotations[self.key].values())
    
    def __len__(self):
        return len(self.annotations[self.key])
    
    def getQuery(self):
        return None
    
    def getTerm(self, value):
        return self.annotations[self.key][value]

    def getTermByToken(self, token):
        return self.getTerm(token)
    
    def add(self, value, title, default=False):
        self.annotations[self.key][value] = SimpleTerm(value, title)
        if default:
            self.default = value

    def delete(self, value):
        if value == self.default.value:
            error_msg = _("Cannot delete default value '${value}'.")
            error_msg.mapping = {'value': value}
            raise ValueError, error_msg
        del self.annotations[self.key][value]

    def _getRealContext(self, context):
        for obj in zapi.getParents(context):
            if self.interface.providedBy(obj):
                return obj
        return context

    def getDefault(self):
        value = self.annotations[self.key+'/default']
        if value is None:
            return None
        return self.getTerm(self.annotations[self.key+'/default'])

    def setDefault(self, value):
        """Set the default value/term. Both, a token and a term are
        accepted."""
        if ITokenizedTerm.providedBy(value):
            value = value.value
        if value not in self:
            error_msg = _("The value '${value}' was not found in the "
                          "vocabulary")
            error_msg.mapping = {'value': value}
            raise ValueError, error_msg
        self.annotations[self.key+'/default'] = value

    default = property(getDefault, setDefault)


class StatusVocabulary(ManagableVocabulary):

    implements(IStatusVocabulary)

    key = 'bugtracker.status.values'
    interface = IBugTracker

    title = _('Status Definitions')


class ReleaseVocabulary(ManagableVocabulary):

    implements(IReleaseVocabulary)

    key = 'bugtracker.release.values'
    interface = IBugTracker

    title = _('Release Definitions')


class PriorityVocabulary(ManagableVocabulary):

    implements(IPriorityVocabulary)

    key = 'bugtracker.priority.values'
    interface = IBugTracker

    title = _('Priority Definitions')


class BugTypeVocabulary(ManagableVocabulary):

    implements(IBugTypeVocabulary)

    key = 'bugtracke.bugtype.values'
    interface = IBugTracker

    title = _('Bug Type Definitions')


class UserTerm(Persistent):

    implements(ITitledTokenizedTerm)

    def __init__(self, principal):
        # This is safe here, since we only read non-critical data
        naked = removeSecurityProxy(principal)
        self.principal = {'id': naked.id,
                          'login': naked.getLogin(),
                          'title': naked.title,
                          'description': naked.description}
        self.value = naked.id
        self.token = naked.id
        self.title = naked.title


class UserVocabulary(object):

    implements(IVocabulary, IVocabularyTokenized)

    def __init__(self, context):
        self.auth = zapi.principals()
    
    def __contains__(self, value):
        ids = map(lambda p: p.id, self.auth.getPrincipals(''))
        return value in ids
    
    def __iter__(self):
        terms = map(lambda p: UserTerm(p), self.auth.getPrincipals(''))
        return iter(terms)
    
    def __len__(self):
        return len(self.auth.getPrincipals(''))
    
    def getQuery(self):
        return None
    
    def getTerm(self, value):
        return UserTerm(self.auth.getPrincipal(value))

    def getTermByToken(self, token):
        return self.getTerm(token)


class VocabularyPropertyGetter(object):
    
    def __init__(self, name, vocab_name):
        self.name = name
        self._vocab_name = vocab_name

    def __call__(self, instance):
        registry = getVocabularyRegistry()
        try:
            vocab = registry.get(instance, self._vocab_name)
            default = vocab.default.value
        except TypeError:
            # We cannot assume that the bug will always have a context to
            # find the vocabulary data. In these cases, we just skip the
            # default lookup.
            default = None
        return getattr(instance, self.name, default)


class VocabularyPropertySetter(object):
    """This generic vocabulary property setter class ensures that the set
    value is in the vocabulary."""
    
    def __init__(self, name, vocab_name):
        self.name = name
        self._vocab_name = vocab_name

    def __call__(self, instance, value):
        registry = getVocabularyRegistry()
        try:
            vocab = registry.get(instance, self._vocab_name)
            if value not in vocab:
                raise ValueError, \
                      "The value '%s' was not found in vocabulary '%s'" %(
                    value, self._vocab_name)
        except TypeError:
            # We cannot assume that the bug will always have a context to
            # find the vocabulary data. In these cases, we just skip the
            # verification.
            vocab = None

        # Make sure the value is a message id
        setattr(instance, self.name, _(value))
