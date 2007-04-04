##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Support for using zope.locking has a locking mechanism for WebDAV locking.

Note that we can't use zope.locking.utility.TokenUtility has a global utility.
This is because if a recursive lock request fails half through then the
utility has already been modified and since it is not persistent
transaction.abort doesn't unlock the pervious successful locks. Since the
utility gets into an inconsistent state.

$Id$
"""
__docformat__ = 'restructuredtext'

import persistent
import time
import random
import datetime
from BTrees.OOBTree import OOBTree
from zope import component
from zope import interface
from zope.locking import tokens
import zope.locking.interfaces
from zope.security.proxy import removeSecurityProxy
from zope.app.keyreference.interfaces import IKeyReference
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.app.container.interfaces import IReadContainer

from zope.webdav.coreproperties import ILockEntry, IDAVSupportedlock, \
     IActiveLock
import zope.webdav.interfaces


INDIRECT_INDEX_KEY = 'zope.app.dav.lockingutils'

_randGen = random.Random(time.time())

class IIndirectToken(zope.locking.interfaces.IToken,
                     zope.locking.interfaces.IEndable):
    """
    """

    roottoken = interface.Attribute("""
    Return the root lock token against which this token is locked.
    """)


class IndirectToken(persistent.Persistent):
    """

    Most of these tests have being copied from the README.txt file in
    zope.locking

    Some initial setup including creating some demo content.

      >>> from zope.locking import utility, utils
      >>> util = utility.TokenUtility()
      >>> component.getGlobalSiteManager().registerUtility(
      ...    util, zope.locking.interfaces.ITokenUtility)

    Setup some content to test on.

      >>> demofolder = DemoFolder(None, 'demofolderroot')
      >>> demofolder['demo1'] = Demo()
      >>> demofolder['demofolder1'] = DemoFolder()
      >>> demofolder['demofolder1']['demo'] = Demo()

    Lock the root folder with an exclusive lock.

      >>> lockroot = tokens.ExclusiveLock(demofolder, 'michael')
      >>> res = util.register(lockroot)

    Now indirectly all the descended objects of the root folder against the
    exclusive lock token we used to lock this folder with.

      >>> lock1 = IndirectToken(demofolder['demo1'], lockroot)
      >>> lock2 = IndirectToken(demofolder['demofolder1'], lockroot)
      >>> lock3 = IndirectToken(demofolder['demofolder1']['demo'], lockroot)
      >>> res1 = util.register(lock1)
      >>> lock1 is util.get(demofolder['demo1'])
      True
      >>> res2 = util.register(lock2)
      >>> lock2 is util.get(demofolder['demofolder1'])
      True
      >>> res3 = util.register(lock3)
      >>> lock3 is util.get(demofolder['demofolder1']['demo'])
      True

    Make sure that the lockroot contains an index of all the toekns locked
    against in its annotations

      >>> len(lockroot.annotations[INDIRECT_INDEX_KEY])
      3

    Check that the IEndable properties are None

      >>> res1.expiration == lockroot.expiration == None
      True
      >>> res1.duration == lockroot.duration == None
      True
      >>> res1.duration == lockroot.remaining_duration == None
      True
      >>> res1.started == lockroot.started
      True
      >>> lockroot.started is not None
      True

    All the indirect locktokens and the lookroot share the same annotations

      >>> lockroot.annotations[u'webdav'] = u'test webdav indirect locking'
      >>> res1.annotations[u'webdav']
      u'test webdav indirect locking'

    All the lock tokens have the same principals

      >>> list(res1.principal_ids)
      ['michael']
      >>> list(lockroot.principal_ids)
      ['michael']

    None of the locks have ended yet, and they share the same utility.

      >>> res1.ended is None
      True
      >>> lockroot.ended is None
      True
      >>> lockroot.utility is res1.utility
      True

    Expire the lock root

      >>> now = utils.now()
      >>> res3.end()

    Now all the descendent objects of the lockroot and the lockroot itself
    are unlocked.

      >>> util.get(demofolder) is None
      True
      >>> util.get(demofolder['demo1']) is None
      True
      >>> util.get(demofolder['demofolder1']['demo']) is None
      True

    Also all the tokens has ended after now.

      >>> lock1.ended is not None
      True
      >>> lock2.ended > now
      True
      >>> lock1.ended is lock2.ended
      True
      >>> lock3.ended is lockroot.ended
      True

    Test the event subscribers.

      >>> ev = events[-1]
      >>> zope.locking.interfaces.ITokenEndedEvent.providedBy(ev)
      True
      >>> len(lockroot.annotations[INDIRECT_INDEX_KEY])
      3
      >>> removeEndedTokens(ev)
      >>> len(lockroot.annotations[INDIRECT_INDEX_KEY])
      0

    Test all the endable attributes

      >>> import datetime
      >>> one = datetime.timedelta(hours = 1)
      >>> two = datetime.timedelta(hours = 2)
      >>> three = datetime.timedelta(hours = 3)
      >>> four = datetime.timedelta(hours = 4)
      >>> lockroot = tokens.ExclusiveLock(demofolder, 'john', three)
      >>> dummy = util.register(lockroot)
      >>> indirect1 = IndirectToken(demofolder['demo1'], lockroot)
      >>> dummy = util.register(indirect1)
      >>> indirect1.duration
      datetime.timedelta(0, 10800)
      >>> lockroot.duration == indirect1.duration
      True
      >>> indirect1.ended is None
      True
      >>> indirect1.expiration == indirect1.started + indirect1.duration
      True

    Now try to 

      >>> indirect1.expiration = indirect1.started + one
      >>> indirect1.expiration == indirect1.started + one
      True
      >>> indirect1.expiration == lockroot.expiration
      True
      >>> indirect1.duration == one
      True

    Now test changing the duration attribute

      >>> indirect1.duration = four
      >>> indirect1.duration == lockroot.duration
      True
      >>> indirect1.duration
      datetime.timedelta(0, 14400)

    Now check the remain_duration code

      >>> import pytz
      >>> def hackNow():
      ...     return (datetime.datetime.now(pytz.utc) +
      ...             datetime.timedelta(hours=2))
      ...
      >>> import zope.locking.utils
      >>> oldNow = zope.locking.utils.now
      >>> zope.locking.utils.now = hackNow # make code think it's 2 hours later
      >>> indirect1.duration
      datetime.timedelta(0, 14400)
      >>> two >= indirect1.remaining_duration >= one
      True
      >>> indirect1.remaining_duration -= one
      >>> one >= indirect1.remaining_duration >= datetime.timedelta()
      True
      >>> three + datetime.timedelta(minutes = 1) >= indirect1.duration >= three
      True

    Since we modified the remaining_duration attribute a IExpirationChagedEvent
    should have being fired.
      
      >>> ev = events[-1]
      >>> from zope.interface.verify import verifyObject
      >>> from zope.locking.interfaces import IExpirationChangedEvent
      >>> verifyObject(IExpirationChangedEvent, ev)
      True
      >>> ev.object is lockroot
      True

    Now pretend that it is a day later, the indirect token and the lock root
    will have timed out sliently.

      >>> def hackNow():
      ...     return (
      ...         datetime.datetime.now(pytz.utc) + datetime.timedelta(days=1))
      ...
      >>> zope.locking.utils.now = hackNow # make code think it is a day later
      >>> indirect1.ended == indirect1.expiration
      True
      >>> lockroot.ended == indirect1.ended
      True
      >>> util.get(demofolder['demo1']) is None
      True
      >>> util.get(demofolder['demo1'], util) is util
      True
      >>> indirect1.remaining_duration == datetime.timedelta()
      True
      >>> indirect1.end()
      Traceback (most recent call last):
      ...
      EndedError

    Once a lock has ended, the timeout can no longer be changed.

      >>> indirect1.duration = datetime.timedelta(days=2)
      Traceback (most recent call last):
      ...
      EndedError

    Now undo our hack.

      >>> zope.locking.utils.now = oldNow # undo the hack
      >>> indirect1.end() # really end the token
      >>> util.get(demofolder) is None
      True

    Now test the simple SharedLock with an indirect token.

      >>> lockroot = tokens.SharedLock(demofolder, ('john', 'mary'))
      >>> dummy = util.register(lockroot)
      >>> sharedindirect = IndirectToken(demofolder['demo1'], lockroot)
      >>> dummy = util.register(sharedindirect)
      >>> sorted(sharedindirect.principal_ids)
      ['john', 'mary']
      >>> sharedindirect.add(('jane',))
      >>> sorted(lockroot.principal_ids)
      ['jane', 'john', 'mary']
      >>> sorted(sharedindirect.principal_ids)
      ['jane', 'john', 'mary']
      >>> sharedindirect.remove(('mary',))
      >>> sorted(sharedindirect.principal_ids)
      ['jane', 'john']
      >>> sorted(lockroot.principal_ids)
      ['jane', 'john']
      >>> lockroot.remove(('jane',))
      >>> sorted(sharedindirect.principal_ids)
      ['john']
      >>> sorted(lockroot.principal_ids)
      ['john']
      >>> sharedindirect.remove(('john',))
      >>> util.get(demofolder) is None
      True
      >>> util.get(demofolder['demo1']) is None
      True

    Test using the shared lock token methods on a non shared lock

      >>> lockroot = tokens.ExclusiveLock(demofolder, 'john')
      >>> dummy = util.register(lockroot)
      >>> indirect1 = IndirectToken(demofolder['demo1'], lockroot)
      >>> dummy = util.register(indirect1)
      >>> dummy is indirect1
      True
      >>> dummy.add('john')
      Traceback (most recent call last):
      ...
      TypeError: can't add a principal to a non-shared token
      >>> dummy.remove('michael')
      Traceback (most recent call last):
      ...
      TypeError: can't add a principal to a non-shared token

    Setup with wrong utility.

      >>> util2 = utility.TokenUtility()
      >>> roottoken = tokens.ExclusiveLock(demofolder, 'michael2')
      >>> roottoken = util2.register(roottoken)
      >>> roottoken.utility == util2
      True

      >>> indirecttoken = IndirectToken(demofolder['demo1'], roottoken)
      >>> indirecttoken = util2.register(indirecttoken)
      >>> indirecttoken.utility is util2
      True
      >>> indirecttoken.utility = util
      Traceback (most recent call last):
      ...
      ValueError: cannot reset utility
      >>> indirecttoken = IndirectToken(demofolder['demo1'], roottoken)
      >>> indirecttoken.utility = util
      Traceback (most recent call last):
      ...
      ValueError: Indirect tokens must be registered withsame utility has the root token

    Cleanup test.

      >>> component.getGlobalSiteManager().unregisterUtility(
      ...    util, zope.locking.interfaces.ITokenUtility)
      True

    """
    interface.implements(IIndirectToken)

    def __init__(self, target, token):
        self.context = self.__parent__ = target
        self.roottoken = token

    _utility = None
    @apply
    def utility():
        # IAbstractToken - this is the only hook I can find since
        # it represents the lock utility in charge of this lock.
        def get(self):
            return self._utility
        def set(self, value):
            if self._utility is not None:
                if value is not self._utility:
                    raise ValueError("cannot reset utility")
            else:
                assert zope.locking.interfaces.ITokenUtility.providedBy(value)
                root = self.roottoken
                if root.utility != value:
                    raise ValueError("Indirect tokens must be registered with" \
                                     "same utility has the root token")
                index = root.annotations.get(INDIRECT_INDEX_KEY, None)
                if index is None:
                    index = root.annotations[INDIRECT_INDEX_KEY] = \
                            tokens.AnnotationsMapping()
                    index.__parent__ = root
                key_ref = IKeyReference(self.context)
                assert index.get(key_ref, None) is None, \
                       "context is already locked"
                index[key_ref] = self
                self._utility = value
        return property(get, set)

    @property
    def principal_ids(self):
        # IAbstractToken
        return self.roottoken.principal_ids

    @property
    def started(self):
        # IAbstractToken
        return self.roottoken.started

    @property
    def annotations(self):
        # See IToken
        return self.roottoken.annotations

    def add(self, principal_ids):
        # ISharedLock
        if not zope.locking.interfaces.ISharedLock.providedBy(self.roottoken):
            raise TypeError, "can't add a principal to a non-shared token"
        return self.roottoken.add(principal_ids)

    def remove(self, principal_ids):
        # ISharedLock
        if not zope.locking.interfaces.ISharedLock.providedBy(self.roottoken):
            raise TypeError, "can't add a principal to a non-shared token"
        return self.roottoken.remove(principal_ids)

    @property
    def ended(self):
        # IEndable
        return self.roottoken.ended

    @apply
    def expiration(): # XXX - needs testing
        # IEndable
        def get(self):
            return self.roottoken.expiration
        def set(self, value):
            self.roottoken.expiration = value
        return property(get, set)

    @apply
    def duration(): # XXX - needs testing
        # IEndable
        def get(self):
            return self.roottoken.duration
        def set(self, value):
            self.roottoken.duration = value
        return property(get, set)

    @apply
    def remaining_duration():
        # IEndable
        def get(self):
            return self.roottoken.remaining_duration
        def set(self, value):
            self.roottoken.remaining_duration = value
        return property(get, set)

    def end(self):
        # IEndable
        return self.roottoken.end()


def removeEndedTokens(event):
    """subscriber handler for ITokenEndedEvent"""
    assert zope.locking.interfaces.ITokenEndedEvent.providedBy(event)
    roottoken = event.object
    assert not IIndirectToken.providedBy(roottoken)
    index = roottoken.annotations.get(INDIRECT_INDEX_KEY, {})
    # read the whole index in memory so that we correctly loop over all the
    # items in this list.
    indexItems = list(index.items())
    for key_ref, token in indexItems:
        # token has ended so it should be removed via the register method
        roottoken.utility.register(token)
        del index[key_ref]

# TODO - need subscriber incase a user tries to add a object has a
# descendent to the lock object.

################################################################################
#
# zope.locking adapters.
#
################################################################################

class ExclusiveLockEntry(object):
    interface.implements(ILockEntry)

    lockscope = [u"exclusive"]
    locktype = [u"write"]


class SharedLockEntry(object):
    interface.implements(ILockEntry)

    lockscope = [u"shared"]
    locktype = [u"write"]


@component.adapter(interface.Interface, zope.webdav.interfaces.IWebDAVRequest)
@interface.implementer(IDAVSupportedlock)
def DAVSupportedlock(context, request):
    ## XXX - not tested.
    utility = component.queryUtility(zope.locking.interfaces.ITokenUtility,
                                     context = context, default = None)
    if utility is None:
        return None
    return DAVSupportedlockAdapter()


class DAVSupportedlockAdapter(object):
    """
      >>> slock = DAVSupportedlockAdapter()
      >>> exclusive, shared = slock.supportedlock

      >>> exclusive.lockscope
      [u'exclusive']
      >>> exclusive.locktype
      [u'write']

      >>> shared.lockscope
      [u'shared']
      >>> shared.locktype
      [u'write']

    """
    interface.implements(IDAVSupportedlock)
    component.adapts(interface.Interface,
                     zope.webdav.interfaces.IWebDAVRequest)

    @property
    def supportedlock(self):
        return [ExclusiveLockEntry(), SharedLockEntry()]


WEBDAV_LOCK_KEY = "zope.webdav.lockingutils.info"

@component.adapter(interface.Interface, zope.webdav.interfaces.IWebDAVMethod)
@interface.implementer(IActiveLock)
def DAVActiveLock(context, request):
    """
    The activelock property only exists whenever the resource is locked.

    XXX - not tested.
    """
    try:
        token = zope.locking.interfaces.ITokenBroker(context).get()
    except TypeError:
        token = None
    if token is None:
        return None
    return DAVActiveLockAdapter(token, context, request)


class DAVActiveLockAdapter(object):
    component.adapts(interface.Interface,
                     zope.webdav.interfaces.IWebDAVRequest)
    interface.implements(IActiveLock)

    def __init__(self, token, context, request):
        self.context = self.__parent__ = context
        self.token = token
        self.request = request

    @property
    def lockscope(self):
        if IIndirectToken.providedBy(self.token):
            roottoken = self.token.roottoken
        else:
            roottoken = self.token

        if zope.locking.interfaces.IExclusiveLock.providedBy(roottoken):
            return [u"exclusive"]
        elif zope.locking.interfaces.ISharedLock.providedBy(roottoken):
            return [u"shared"]

        raise ValueError("Unknow lock token used for locking")

    @property
    def locktype(self):
        return [u"write"]

    @property
    def depth(self):
        return self.token.annotations[WEBDAV_LOCK_KEY]["depth"]

    @property
    def owner(self):
        return self.token.annotations[WEBDAV_LOCK_KEY]["owner"]

    @property
    def timeout(self):
        return u"Second-%d" % self.token.remaining_duration.seconds

    @property
    def locktoken(self):
        return [self.token.annotations[WEBDAV_LOCK_KEY]["token"]]

    @property
    def lockroot(self):
        if IIndirectToken.providedBy(self.token):
            root = self.token.roottoken.context
        else:
            root = self.token.context

        return absoluteURL(root, self.request)


@component.adapter(interface.Interface, zope.webdav.interfaces.IWebDAVRequest)
@interface.implementer(zope.webdav.coreproperties.IDAVLockdiscovery)
def DAVLockdiscovery(context, request):
    utility = component.queryUtility(zope.locking.interfaces.ITokenUtility)
    if utility is None:
        return None
    return DAVLockdiscoveryAdapter(context, request)


class DAVLockdiscoveryAdapter(object):
    interface.implements(zope.webdav.coreproperties.IDAVLockdiscovery)
    component.adapts(interface.Interface,
                     zope.webdav.interfaces.IWebDAVRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def lockdiscovery(self):
        adapter = component.queryMultiAdapter((self.context, self.request),
                                              IActiveLock, default = None)
        if adapter is None:
            return None
        return [adapter]


class DAVLockmanager(object):
    """

      >>> from zope.interface.verify import verifyObject
      >>> from zope.locking import utility, utils
      >>> from zope.locking.adapters import TokenBroker

      >>> file = Demo()

    Before we register a ITokenUtility utility make sure that the DAVLockmanager
    is not lockable.

      >>> adapter = DAVLockmanager(file)
      >>> adapter.islockable()
      False

    Now create and register a ITokenUtility utility.

      >>> util = utility.TokenUtility()
      >>> component.getGlobalSiteManager().registerUtility(
      ...    util, zope.locking.interfaces.ITokenUtility)
      >>> component.getGlobalSiteManager().registerAdapter(
      ...    TokenBroker, (interface.Interface,),
      ...    zope.locking.interfaces.ITokenBroker)

      >>> import pytz
      >>> def hackNow():
      ...     return datetime.datetime(2006, 7, 25, 23, 49, 51)
      >>> oldNow = utils.now
      >>> utils.now = hackNow

    Test the DAVLockmanager implements the descired interface.

      >>> adapter = DAVLockmanager(file)
      >>> verifyObject(zope.webdav.interfaces.IDAVLockmanager, adapter)
      True

    The adapter should also be lockable.

      >>> adapter.islockable()
      True

    Lock with an exclusive lock token.

      >>> roottoken = adapter.lock(u'exclusive', u'write',
      ...    u'Michael', datetime.timedelta(seconds = 3600), '0')
      >>> util.get(file) == roottoken
      True
      >>> zope.locking.interfaces.IExclusiveLock.providedBy(roottoken)
      True

      >>> adapter.islocked()
      True

      >>> activelock = adapter.getActivelock()
      >>> activelock.lockscope
      [u'exclusive']
      >>> activelock.locktype
      [u'write']
      >>> activelock.depth
      '0'
      >>> activelock.timeout
      u'Second-3600'
      >>> activelock.lockroot
      '/dummy'
      >>> activelock.owner
      u'Michael'

      >>> adapter.refreshlock(datetime.timedelta(seconds = 7200))
      >>> adapter.getActivelock().timeout
      u'Second-7200'

      >>> adapter.unlock()
      >>> util.get(file) is None
      True
      >>> adapter.islocked()
      False
      >>> adapter.getActivelock() is None
      True

    Shared locking support.

      >>> roottoken = adapter.lock(u'shared', u'write', u'Michael',
      ...    datetime.timedelta(seconds = 3600), '0')
      >>> util.get(file) == roottoken
      True
      >>> zope.locking.interfaces.ISharedLock.providedBy(roottoken)
      True

      >>> activelock = adapter.getActivelock()
      >>> activelock.lockscope
      [u'shared']
      >>> activelock.locktoken #doctest:+ELLIPSIS
      ['opaquelocktoken:...

      >>> adapter.unlock()

    Recursive lock suport.

      >>> demofolder = DemoFolder()
      >>> demofolder['demo'] = file

      >>> adapter = DAVLockmanager(demofolder)
      >>> roottoken = adapter.lock(u'exclusive', u'write', u'MichaelK',
      ...    datetime.timedelta(seconds = 3600), 'infinity')

      >>> demotoken = util.get(file)
      >>> IIndirectToken.providedBy(demotoken)
      True

      >>> activelock = adapter.getActivelock()
      >>> activelock.lockroot
      '/dummy/'
      >>> DAVLockmanager(file).getActivelock().lockroot
      '/dummy/'
      >>> absoluteURL(file, None)
      '/dummy/dummy'
      >>> activelock.lockscope
      [u'exclusive']

    Already locked support.

      >>> adapter.lock(u'exclusive', u'write', u'Michael',
      ...    datetime.timedelta(seconds = 100), 'infinity') #doctest:+ELLIPSIS
      Traceback (most recent call last):
      ...
      AlreadyLocked...
      >>> adapter.islocked()
      True

      >>> adapter.unlock()

    Some error conditions.

      >>> adapter.lock(u'exclusive', u'notwrite', u'Michael',
      ...    datetime.timedelta(seconds = 100), 'infinity') # doctest:+ELLIPSIS
      Traceback (most recent call last):
      ...
      UnprocessableError: ...

      >>> adapter.lock(u'notexclusive', u'write', u'Michael',
      ...    datetime.timedelta(seconds = 100), 'infinity') # doctest:+ELLIPSIS
      Traceback (most recent call last):
      ...
      UnprocessableError: ...

      >>> component.getGlobalSiteManager().unregisterUtility(
      ...    util, zope.locking.interfaces.ITokenUtility)
      True
      >>> component.getGlobalSiteManager().unregisterAdapter(
      ...    TokenBroker, (interface.Interface,),
      ...    zope.locking.interfaces.ITokenBroker)
      True
      >>> utils.now = oldNow

    """
    interface.implements(zope.webdav.interfaces.IDAVLockmanager)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = self.__parent__ = context

    def generateLocktoken(self):
        return "opaquelocktoken:%s-%s-00105A989226:%.03f" % \
               (_randGen.random(), _randGen.random(), time.time())

    def islockable(self):
        utility = component.queryUtility(zope.locking.interfaces.ITokenUtility,
                                         context = self.context, default = None)
        return utility is not None

    def lock(self, scope, type, owner, duration, depth,
             roottoken = None, context = None):
        if type != u"write":
            raise zope.webdav.interfaces.UnprocessableError(
                self.context,
                message = "Invalid locktype supplied to lock manager.")

        if context is None:
            context = self.context

        tokenBroker = zope.locking.interfaces.ITokenBroker(context)
        if tokenBroker.get():
            raise zope.webdav.interfaces.AlreadyLocked(
                context, message = u"Context or subitem is already locked.")

        if roottoken is None:
            if scope == u"exclusive":
                roottoken = tokenBroker.lock(duration = duration)
            elif scope == u"shared":
                roottoken = tokenBroker.lockShared(duration = duration)
            else:
                raise zope.webdav.interfaces.UnprocessableError(
                    self.context,
                    message = u"Invalid lockscope supplied to the lock manager")

            annots = roottoken.annotations.get(WEBDAV_LOCK_KEY, None)
            if annots is None:
                annots = roottoken.annotations[WEBDAV_LOCK_KEY] = OOBTree()
            annots["owner"] = owner
            annots["token"] = self.generateLocktoken()
            annots["depth"] = depth
        else:
            indirecttoken = IndirectToken(context, roottoken)
            ## XXX - using removeSecurityProxy - is this right, has
            ## it seems wrong
            removeSecurityProxy(roottoken).utility.register(indirecttoken)

        if depth == "infinity" and IReadContainer.providedBy(context):
            for subob in context.values():
                self.lock(scope, type, owner, duration, depth,
                          roottoken, subob)

        return roottoken

    def getActivelock(self, request = None):
        if self.islocked():
            token = zope.locking.interfaces.ITokenBroker(self.context).get()
            return DAVActiveLockAdapter(token, self.context, request)
        return None

    def refreshlock(self, timeout):
        token = zope.locking.interfaces.ITokenBroker(self.context).get()
        token.duration = timeout

    def unlock(self):
        tokenBroker = zope.locking.interfaces.ITokenBroker(self.context)
        token = tokenBroker.get()
        token.end()

    def islocked(self):
        tokenBroker = zope.locking.interfaces.ITokenBroker(self.context)
        return tokenBroker.get() is not None
