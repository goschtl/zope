##############################################################################
#
# Copyright (c) 2002-2006 Zope Corporation and Contributors.
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
"""
$Id$
"""

import logging

from persistent import Persistent
from ZODB.POSException import ConflictError

logger = logging.getLogger(__name__)

SAFE_POLICY = 0
ALTERNATIVE_POLICY = 1

REMOVED       = 0
ADDED         = 1
CHANGED       = 2
CHANGED_ADDED = 3
EVENT_TYPES = (REMOVED, CHANGED, ADDED, CHANGED_ADDED)
antiEvent = {REMOVED:       ADDED,
             ADDED:         REMOVED,
             CHANGED:       CHANGED,
             CHANGED_ADDED: CHANGED_ADDED,
             }.get

ADDED_EVENTS = (CHANGED, ADDED, CHANGED_ADDED)

class CatalogEventQueue(Persistent):
    """Event queue for catalog events

    This is a rather odd queue. It organizes events by object, where
    objects are identified by uids, which happen to be string paths.

    One way that this queue is extremely odd is that it really only
    keeps track of the last event for an object. This is because we
    really only *care* about the last event for an object.

    There are three types of events:

    ADDED         -- An object was added to the catalog

    CHANGED       -- An object was changed

    REMOVED       -- An object was removed from the catalog

    CHANGED_ADDED -- Add object was added and subsequently changed.
                     This event is a consequence of the queue implementation.


        |---------------------------------------------|
        V                                             V
    ->[ADDED]-- change -->[CHANGED_ADDED]--remove-->[REMOVED]<-
                             ^     |                   ^
                             |     |                   |
                              change                [CHANGED]<-
                                                     ^    |
                                                     |    ]
                                                     change


    Note that, although we only keep track of the most recent
    event. there are rules for how the most recent event can be
    updated:

    - It is illegal to update an ADDED, CHANGED, or CHANGED_ADDED
      event with an ADDED event or

    - to update a REMOVED event with a CHANGED event.

    We have a problem because applications don't really indicate
    whether they are are adding, or just updating.  We deduce add
    events by examining the catalog and event queue states.

    Also note that, when events are applied to the catalog, events may
    have no effect.

    - If an object is in the catalog, ADDED events are equivalent to
      CHANGED events.

    - If an object is not in the catalog, REMOVED and CHANGED events
      have no effect.

    If we undo a transaction, we generate an anti-event. The anti
    event of ADDED is REMOVED, of REMOVED is ADDED, and of CHANGED is
    CHANGED.

    Note that these rules represent heuristics that attempt to provide
    efficient and sensible behavior for most cases. They are not "correct" in
    that they handle cases that may not seem handleable. For example,
    consider a sequence of transactions:

      T1 adds an object
      T2 removes the object
      T3 adds the object
      T4 processes the queue
      T5 undoes T1

    It's not clear what should be done in this case? We decide to
    generate a remove event, even though a later transaction added the
    object again. Is this correct? It's hard to say. The decision we
    make is not horrible and it allows us to provide a very efficient
    implementation.  See the unit tests for other scenarios. Feel
    free to think of cases for which our decisions are unacceptably
    wrong and write unit tests for these cases.

    There are two kinds of transactions that affect the queue:

    - Application transactions always add or modify events. They never
      remove events.

    - Queue processing transactions always remove events.

    """

    _conflict_policy = SAFE_POLICY
    _generation = 0

    def __init__(self, conflict_policy=SAFE_POLICY):

        # Mapping from uid -> (generation, event type)
        self._data = {}
        self._conflict_policy = conflict_policy

    def __nonzero__(self):
        return not not self._data

    def __len__(self):
        return len(self._data)

    def update(self, uid, etype):
        assert etype in EVENT_TYPES
        data = self._data
        current = data.get(uid)

        if current is not None:
            _, current = current
            if current in ADDED_EVENTS and etype is ADDED:
                raise TypeError("Attempt to add an object that is already "
                                "in the catalog")
            if current is REMOVED and etype is CHANGED:
                raise TypeError("Attempt to change an object that has "
                                "been removed")

            if ((current is ADDED or current is CHANGED_ADDED)
                and etype is CHANGED):
                etype = CHANGED_ADDED

            if etype == current:
                return 0 # no change

        data[uid] = 0, etype
        self._generation += 1
        return 1

    def getEvent(self, uid):
        state = self._data.get(uid)
        if state is not None:
            state = state[1]
        return state

    def process(self, limit=None):
        """Removes and returns events from this queue.

        If limit is specified, at most (limit) events are removed.
        """
        data = self._data
        if not limit or len(data) <= limit:
            self._data = {}
            return data
        else:
            self._p_changed = 1
            res = {}
            keys = data.keys()[:limit]
            for key in keys:
                res[key] = data[key]
                del data[key]
            return res

    def _p_resolveConflict(self, oldstate, committed, newstate):
        # Apply the changes made in going from old to newstate to
        # committed

        # Note that in the case of undo, the olddata is the data for
        # the transaction being undone and newdata is the data for the
        # transaction previous to the undone transaction. In this
        # case, the old generation will be larger than the new.

        # Find the conflict policy on the new state to make sure changes
        # to it will be applied
        policy = newstate['_conflict_policy']

        # Committed is always the currently committed data.
        oldstate_data  =  oldstate['_data']
        committed_data = committed['_data']
        newstate_data  =  newstate['_data']

        try:
            newgen = newstate['_generation']
            oldgen = oldstate['_generation']
        except KeyError:
            logger.error('Queue conflict %r: no generation data.', uid)
            raise ConflictError

        changes = {}

        if newgen < oldgen:
            # Undo
            #
            # newstate is a previous revision of oldstate.  That is,
            # oldstate is a later generation of newstate.


            for uid, new in newstate_data.iteritems():
                # If newstate has items not in old state, then that
                # means that oldstate processed some events.  We don't
                # care about undo support for processing of old events.
                if uid not in oldstate:
                    # undo of processing event, give up:
                    logger.error('Queue conflict %r: undo processing.', uid)

            for uid, old in oldstate_data.iteritems():
                # cases:
                # - events in oldstatate not in new state. These are
                #   events added by old transaction. To undo them, we
                #   we need anti events.
                # - events that are in both old and new, but that are
                #   different.  Apply the anti event of old
                # - events are same in old and new, ignore

                new = newstate_data.get(uid)
                if new == old:
                    continue
                changes[uid] = antiEvent[old[1]]

        else:
            # Non undo.
            #
            # cases:
            # - in old, but not in new. This means the new transaction
            #   processed the old event.  We can ignore these cases.
            # - in new, but not in old.  We need to include these
            #   in the changes.
            # - same in old and new. Not a change, ignore.
            #   Different.  Apply the change (if we can).
            for uid, new in newstate_data.iteritems():
                old = oldstate_data.get(uid)
                if old == new:
                    continue
                changes[uid] = new[1]

        # OK, now we have a set of changes. See if we can combine them with
        # the current.
        for uid, change in changes.iteritems():
            committed = committed_data.get(uid)
            if committed is None:
                # Not in committed data.  We don't know what happened.
                # Can't guess
                logger.error(
                    "Queue conflict on %s: Can't guess about new event" % uid)
                raise ConflictError
            if committed == change:
                continue
            _, committed = committed
            _, change = change
            if committed == REMOVED or change == REMOVED:
                logger.error(
                    "Queue conflict on %s: Change to removed data" % uid)
                raise ConflictError
            committed_data[uid] = 0, change

        return { '_data': committed_data
               , '_conflict_policy' : policy
               }

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self._data)

__doc__ = CatalogEventQueue.__doc__ + __doc__
