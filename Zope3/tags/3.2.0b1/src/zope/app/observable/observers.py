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
"""Observer Registry

`Observers` observe other objects by getting notified of object events
on those objects. `Observers` subscribe to particular types of events.

  >>> registry = Observers()

  >>> import zope.interface
  >>> class IR1(zope.interface.Interface):
  ...     pass
  >>> class IP1(zope.interface.Interface):
  ...     pass
  >>> class IP2(IP1):
  ...     pass
  >>> class IQ(zope.interface.Interface):
  ...     pass

  >>> registry.subscribe([IR1], IP2, 'sub12 1')
  >>> registry.subscriptions([IR1], IP2)
  ['sub12 1']

You can have multiple subscribers for the same specification::

  >>> registry.subscribe([IR1], IP2, 'sub12 2')
  >>> subs = registry.subscriptions([IR1], IP2)
  >>> subs.sort()
  >>> subs
  ['sub12 1', 'sub12 2']

You can register subscribers for all specifications using ``None``::

  >>> class IR2(IR1):
  ...     pass

  >>> registry.subscribe([None], IP1, 'sub_1')
  >>> subs = registry.subscriptions([IR2], IP1)
  >>> subs.sort()
  >>> subs
  ['sub12 1', 'sub12 2', 'sub_1']

Subscriptions may be combined over multiple compatible specifications::

  >>> subs = registry.subscriptions([IR2], IP1)
  >>> subs.sort()
  >>> subs
  ['sub12 1', 'sub12 2', 'sub_1']
  >>> registry.subscribe([IR1], IP1, 'sub11')
  >>> subs = registry.subscriptions([IR2], IP1)
  >>> subs.sort()
  >>> subs
  ['sub11', 'sub12 1', 'sub12 2', 'sub_1']
  >>> registry.subscribe([IR2], IP2, 'sub22')
  >>> subs = registry.subscriptions([IR2], IP1)
  >>> subs.sort()
  >>> subs
  ['sub11', 'sub12 1', 'sub12 2', 'sub22', 'sub_1']
  >>> subs = registry.subscriptions([IR2], IP2)
  >>> subs.sort()
  >>> subs
  ['sub12 1', 'sub12 2', 'sub22']

Subscriptions can be on multiple specifications::

  >>> class IQ(zope.interface.Interface):
  ...     pass

  >>> registry.subscribe([IR1, IQ], IP2, 'sub1q2')
  >>> registry.subscriptions([IR1, IQ], IP2)
  ['sub1q2']
  
As with single subscriptions, you can specify None for the first
required interface, to specify a default::

  >>> registry.subscribe([None, IQ], IP2, 'sub_q2')

  >>> class IS(zope.interface.Interface):
  ...     pass

  >>> registry.subscriptions([IS, IQ], IP2)
  ['sub_q2']
  >>> subs = registry.subscriptions([IR1, IQ], IP2)
  >>> subs.sort()
  >>> subs
  ['sub1q2', 'sub_q2']

You can unsubscribe:

  >>> registry.unsubscribe([IR1], IP2, 'sub12 2')
  >>> subs = registry.subscriptions([IR2], IP1)
  >>> subs.sort()
  >>> subs
  ['sub11', 'sub12 1', 'sub22', 'sub_1']
    
$Id$  
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from zope.interface.adapter import Default, Null
from zope.interface.adapter import Surrogate, AdapterRegistry

class LocalSurrogate(Surrogate):
    """Local surrogates

    Local surrogates are transient, rather than persistent.

    Their adapter data are stored in their registry objects.
    """

    def __init__(self, spec, registry):
        super(LocalSurrogate, self).__init__(spec, registry)
        self.registry = registry

    def clean(self):
        spec = self.spec()
        ladapters = self.registry.adapters.get(spec)
        if ladapters:
            self.adapters = dict(
                [((True, required, '', provided), subs)
                 for ((required, provided), subs) in ladapters.iteritems()
                 ]
                )
        else:
            self.adapters = {}
        super(LocalSurrogate, self).clean()

class Observers(AdapterRegistry, Persistent):
    """Local/persistent surrogate registry
    """
    
    _surrogateClass = LocalSurrogate

    def __init__(self):
        self.adapters = {}
        super(Observers, self).__init__()

    def __getstate__(self):
        state = Persistent.__getstate__(self).copy()

        # set by AdapterRegistry.__init__
        del state['_default']
        del state['_null']

        # the following attributes are instance methods that
        # AdapterRegistry.__init__ took from its AdapterLookup
        # instance
        for key in ('lookup', 'lookup1', 'queryAdapter', 'get',
                    'adapter_hook', 'subscriptions',
                    'queryMultiAdapter', 'subscribers'):
            del state[key]
        return state

    def __setstate__(self, state):
        Persistent.__setstate__(self, state)
        AdapterRegistry.__init__(self)

    def subscribe(self, required, provided, subscriber):
        if len(required) == 0:
            raise ValueError("required can not be zero length")

        if provided is None:
            provided = Null

        akey = required[0]
        if akey is None:
            akey = Default
        adapters = self.adapters.get(akey)
        if not adapters:
            adapters = self.adapters[akey] = {}
        key = tuple(required[1:]), provided
        adapters[key] = adapters.get(key, ()) + (subscriber, )

        # reinitialize, thus clearing surrogates *and* marking as changed :)
        AdapterRegistry.__init__(self)

    def unsubscribe(self, required, provided, subscriber):
        if provided is None:
            provided = Null

        akey = required[0]
        if akey is None:
            akey = Default
        adapters = self.adapters.get(akey)
        if not adapters:
            return

        key = tuple(required[1:]), provided
        subscribers = adapters.get(key, ())
        if subscriber in subscribers:
            subscribers = list(subscribers)
            subscribers.remove(subscriber)
            if subscribers:
                adapters[key] = tuple(subscribers)
            else:
                del adapters[key]

            # reinitialize, thus clearing surrogates *and* marking as changed
            AdapterRegistry.__init__(self)
            self._p_changed = True
