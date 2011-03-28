##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""list container

$Id: listcontainer.py 2636 2005-07-06 22:30:43Z gary $
"""
from UserList import UserList

from persistent.list import PersistentList
from zope import interface
from zope.event import notify
from zope.component.interfaces import ObjectEvent

import interfaces

class ObjectMovedEvent(ObjectEvent):
    """An object has been moved among list containers"""

    interface.implements(interfaces.IObjectMovedEvent)

    def __init__(self, object, oldSuper, oldPrevious, oldNext, newSuper,
                 newPrevious, newNext):
        ObjectEvent.__init__(self, object)
        self.oldSuper = oldSuper
        self.oldPrevious = oldPrevious
        self.oldNext = oldNext
        self.newSuper = newSuper
        self.newPrevious = newPrevious
        self.newNext = newNext

class ObjectAddedEvent(ObjectMovedEvent):
    """An object has been added to a list container"""

    interface.implements(interfaces.IObjectAddedEvent)

    def __init__(self, object, newSuper=None, newPrevious=None, newNext=None):
        if newSuper is None:
            newSuper = object.super
        if newPrevious is None:
            newPrevious = object.previous
        if newNext is None:
            newNext = object.next
        ObjectMovedEvent.__init__(
            self, object, None, None, None, newSuper, newPrevious, newNext)

class ObjectReorderedEvent(ObjectEvent):
    """An object's predecessor has changed but not its super"""

    interface.implements(interfaces.IObjectReorderedEvent)

    def __init__(self, object, oldPrevious, oldNext, super=None,
                 newPrevious=None, newNext=None):
        ObjectEvent.__init__(self, object)
        if super is None:
            super = object.super
        if newPrevious is None:
            newPrevious = object.previous
        if newNext is None:
            newNext = object.next
        self.oldSuper = super
        self.oldPrevious = oldPrevious
        self.oldNext = oldNext
        self.newSuper = super
        self.newPrevious = newPrevious
        self.newNext = newNext
class ObjectRemovedEvent(ObjectMovedEvent):
    """An object has been removed from a list container"""

    interface.implements(interfaces.IObjectRemovedEvent)

    def __init__(self, object, oldSuper=None, oldPrevious=None, oldNext=None):
        if oldSuper is None:
            oldSuper = object.super
        if oldPrevious is None:
            oldPrevious = object.previous
        if oldNext is None:
            oldNext = object.next
        ObjectMovedEvent.__init__(
            self, object, oldSuper, oldPrevious, oldNext, None, None, None)

class ObjectReplacedEvent(ObjectRemovedEvent):
    """An object has been replaced within a list container"""

    interface.implements(interfaces.IObjectReplacedEvent)

    def __init__(
        self, object, replacement, oldSuper=None, oldPrevious=None,
        oldNext=None, replacementOldSuper=None, replacementOldPrevious=None,
        replacementOldNext=None, replacementNewSuper=None,
        replacementNewPrevious=None, replacementNewNext=None):
        super(ObjectReplacedEvent, self).__init__(
            object, oldSuper, oldPrevious, oldNext)
        if replacementNewSuper is None:
            replacementNewSuper = replacement.super
        if replacementNewPrevious is None:
            replacementNewPrevious = replacement.previous
        if replacementNewNext is None:
            replacementNewNext = replacement.next
        self.replacement = replacement
        self.replacementOldSuper = replacementOldSuper
        self.replacementOldPrevious = replacementOldPrevious
        self.replacementOldNext = replacementOldNext
        self.replacementNewSuper = replacementNewSuper
        self.replacementNewPrevious = replacementNewPrevious
        self.replacementNewNext = replacementNewNext

def uniquify(items, move=True):
    found = set()
    res = []
    for item in items:
        assert interfaces.IContained.providedBy(item)
        if not move and item.super is not None:
            raise RuntimeError(
                "Cannot add items that already have a super", item)
        iid = id(item)
        if iid not in found:
            res.append(item)
        found.add(iid)
    return res

class Contained(object):
    interface.implements(interfaces.IContained)
    super = next = previous = None

class ListContainer(PersistentList):
    interface.implements(interfaces.IListContainer)

    def __init__(self, initlist=None):
        super(ListContainer, self).__init__()
        if initlist is not None:
            self.extend(initlist)

    def _after_add(
        self, item, oldSuper, oldPrevious, oldNext, super, previous, next):
        item.super = super
        item.previous = previous
        item.next = next
        if previous is not None:
            previous.next = item
        events = []
        if next is not None:
            if next.previous is not item:
                events.append(ObjectReorderedEvent(
                    next, next.previous, next.next, next.super, item))
                next.previous = item
        if oldNext is not None:
            oldNextNext = oldNext.next
            if oldNextNext is item:
                # urk.  guess.
                oldNextNext = item.next
            events.append(ObjectReorderedEvent(
                oldNext, item, oldNextNext, oldNext.super,
                oldNext.previous, oldNext.next))
        if oldSuper is not None:
            if oldSuper is not self:
                events.insert(0, ObjectMovedEvent(
                    item, oldSuper, oldPrevious, oldNext, self, previous,
                    next))
            elif oldPrevious is not previous:
                events.insert(0, ObjectReorderedEvent(
                    item, oldPrevious, oldNext, self, previous, next))
        else:
            events.insert(0, ObjectAddedEvent(item))
        return events

    def _after_multi_add(self, items, previous, next, i):
        moved = set()
        added = set()
        participants = dict(
            [(id(item), (item, item.super, item.previous, item.next))
            for item in items])
        while next is not None and id(next) in participants:
            next = next.next
        if next is not None:
            iid = id(next)
            participants[iid] = (next, next.super, next.previous, next.next)
            moved.add(iid)
        while previous is not None and id(previous) in participants:
            previous = previous.previous
        if previous is not None:
            participants[id(previous)] = (
                previous, previous.super, previous.previous, previous.next)
        initialPrevious = previous
        if i < 0:
            i = len(self) + i
        for item in items:
            if item.super:
                index = item.super.index(item)
                if item.super is self: # :-(
                    # readd afterindex ???
                    if index >= i:
                        # we don't want one in the middle of the added bit.
                        # we guarantee that all items in items are unique
                        # elsewhere, so we should just be able to get the next
                        # one
                        index = item.super.index(item, index+1)
                    moved.add(id(item))
                    if (item.previous is not None and
                        item.previous is not initialPrevious):
                        item.previous.next = item.next
                    if item.next is not None:
                        n = item.next
                        n.previous = item.previous
                        iid = id(n)
                        if iid not in participants:
                            participants[iid] = (
                                n, n.super, n.previous, n.next)
                        moved.add(iid)
                    super(ListContainer, self).pop(index)
                else:
                    moved.add(id(item))
                    if item.next is not None:
                        n = item.next
                        n.previous = item.previous
                        iid = id(n)
                        if iid not in participants:
                            participants[iid] = (
                                n, n.super, n.previous, n.next)
                        moved.add(iid)
                    item.super.silentpop(index)
            else:
                added.add(id(item))
            if previous is not None:
                previous.next = item
            item.previous = previous
            item.super = self
            previous = item
        item.next = next
        if next is not None:
            next.previous = item
        for iid in moved:
            item, oldSuper, oldPrevious, oldNext = participants[iid]
            if oldSuper is not self:
                notify(ObjectMovedEvent(
                    item, oldSuper, oldPrevious, oldNext, self, item.previous,
                    item.next))
            elif oldPrevious is not item.previous:
                notify(ObjectReorderedEvent(
                    item, oldPrevious, oldNext, self, item.previous,
                    item.next))
        for iid in added:
            item, oldSuper, oldPrevious, oldNext = participants[iid]
            notify(ObjectAddedEvent(item))

    def _after_rearrange(self):
        data = []
        previous = item = None
        for item in self:
            data.append((item, item.previous, item.next))
            item.previous = previous
            if previous is not None:
                previous.next = item
            previous = item
        if item is not None:
            item.next = None
        for item, previous, next in data:
            if item.previous is not previous:
                notify(ObjectReorderedEvent(
                    item, previous, next, self, item.previous, item.next))

    def silentpop(self, i=-1):
        try:
            current = self[i]
        except IndexError:
            pass # let the super call raise the right error
        else:
            assert current.super is self
            if current.previous is not None:
                current.previous.next = current.next
            if current.next is not None:
                current.next.previous = current.previous
            current.super = current.previous = current.next = None
        return super(ListContainer, self).pop(i)

    def index(self, item, *args):
        if len(args) > 2:
            raise ValueError("too many arguments")
        start, stop = args + (None,) * (2-len(args))
        if start is not None:
            if stop is not None:
                items = self[start:stop]
            else:
                items = self[start:]
        else:
            start = 0
            items = self
        for ix, i in enumerate(items):
            if item is i:
                return ix + start
        raise ValueError("list.index(x): x not in list")

    def moveinsert(self, i, *items):
        next = self[i] # let this raise an error because the slice won't
        if not items:
            return
        items = uniquify(items)
        self.data[i:i] = items
        self._p_changed = 1
        self._after_multi_add(items, next.previous, next, i)

    def moveappend(self, item):
        assert interfaces.IContained.providedBy(item)
        oldSuper = item.super
        oldPrevious = item.previous
        oldNext = item.next
        if self: # assumes boolean "hasChildren==True" behavior
            previous = self[-1]
        else:
            previous = None
        if oldSuper is not None:
            oldIndex = oldSuper.index(item)
            if oldSuper is self and previous is item:
                return None # noop
            oldSuper.silentpop(oldIndex)
        super(ListContainer, self).append(item)
        for ev in self._after_add(
            item, oldSuper, oldPrevious, oldNext, self, previous, None):
            notify(ev)

    def movereplace(self, i, item):
        assert interfaces.IContained.providedBy(item)
        current = None
        try:
            current = self[i]
        except IndexError:
            pass # let the super call raise the right error
        else:
            if current is item:
                return # noop
            oldSuper = item.super
            oldPrevious = item.previous
            oldNext = item.next
            next = current.next
            realPrevious = previous = current.previous
            if previous is item:
                previous = item.previous
            if oldSuper is not None:
                oldIndex = oldSuper.index(item)
                if oldSuper is self and oldIndex < i:
                    i -= 1
                oldSuper.silentpop(oldIndex)
        super(ListContainer, self).__setitem__(i, item)
        if current.super is self:
            current.super = current.previous = current.next = None
        events = self._after_add(
            item, oldSuper, oldPrevious, oldNext, self, previous, next)
        notify(ObjectReplacedEvent(
            current, item, self, realPrevious, next,
            oldSuper, oldPrevious, oldNext))
        if current is oldNext:
            events.pop()
        for ev in events:
            notify(ev)

    def __iter__(self):
        return iter(self.data)

    def __setitem__(self, i, item):
        if not isinstance(i, int):
            raise NotImplementedError # probably a slice XXX
        assert interfaces.IContained.providedBy(item)
        if item.super is not None:
            raise RuntimeError(
                "Cannot set item that already has a super")
        self.movereplace(i, item)

    def __delitem__(self, i):
        if not isinstance(i, int):
            # let's hope it's a slice
            ix, stop, step = i.indices(len(self))
            if step < 0:
                while ix > stop:
                    self.pop(ix)
                    ix += step
            else:
                while ix < stop:
                    self.pop(ix)
                    stop -= 1
                    ix += step-1
        else:
            self.pop(i)

    def pop(self, i=-1):
        try:
            current = self[i]
        except IndexError:
            pass # let the super call raise the right error
        else:
            assert current.super is self
            if current.previous is not None:
                current.previous.next = current.next
            if current.next is not None:
                next = current.next
                notify(ObjectReorderedEvent(
                    next, next.previous, next.next,
                    next.super, current.previous, next.next))
                next.previous = current.previous
            notify(ObjectRemovedEvent(current))
            current.super = current.previous = current.next = None
        return super(ListContainer, self).pop(i)

    def append(self, item):
        assert interfaces.IContained.providedBy(item)
        if item.super is not None:
            raise RuntimeError(
                "Cannot append item that already has a super")
        self.moveappend(item)

    def insert(self, i, item):
        assert interfaces.IContained.providedBy(item)
        if item.super is not None:
            raise RuntimeError(
                "Cannot insert item that already has a super")
        self.moveinsert(i, item)

    def remove(self, item):
        self.pop(self.index(item))

    def __delslice__(self, i, j): # don't support step
        old = self[i:j]
        if old: # else noop
            del self.data[i:j]
            self._p_changed = 1
            previous = old[0].previous
            next = old[-1].next
            if previous is not None:
                previous.next = next
            if next is not None:
                notify(ObjectReorderedEvent(
                    next, next.previous, next.next,
                    next.super, previous, next.next))
                next.previous = previous
            for item in old:
                assert item.super is self
                notify(ObjectRemovedEvent(item))
                item.super = item.previous = item.next = None

    def extend(self, other):
        items = uniquify(other, move=False)
        if self:
            previous = self[-1]
        else:
            previous = None
        if items:
            i = len(self)
            super(ListContainer, self).extend(items)
            self._after_multi_add(items, previous, None, i)

    def moveextend(self, other):
        items = uniquify(other)
        if self:
            previous = self[-1]
        else:
            previous = None
        if items:
            i = len(self)
            super(ListContainer, self).extend(items)
            self._after_multi_add(items, previous, None, i)

    __iadd__ = extend

    def __imul__(self, n):
        raise TypeError('does not support in-place multiplication')
        # ...and I do not intend it to (which is why this is a TypeError,
        # not a NotImplemented error)
    
    def __contains__(self, item):
        for i in self:
            if i is item:
                return True
        return False
    
    def count(self, item):
        return int(item in self) # 0 or 1

    def __add__(self, other):
        # return the raw data, not a class instance
        if isinstance(other, UserList):
            return self.data + other.data
        elif isinstance(other, type(self.data)):
            return self.data + other
        else:
            return self.data + list(other)

    def __radd__(self, other):
        # return the raw data, not a class instance
        if isinstance(other, UserList):
            return other.data + self.data
        elif isinstance(other, type(self.data)):
            return other + self.data
        else:
            return list(other) + self.data

    def __mul__(self, n):
        # return the raw data, not a class instance
        return self.data*n

    def __getslice__(self, i, j):
        # return the raw data, not a class instance; do not limit to non-
        # negative slices.
        return self.data[i:j]

    def __setslice__(self, i, j, other):
        self.__delslice__(i, j) # XXX could try for replace event...
        items = uniquify(other, move=False)
        if not items:
            return
        try:
            next = self[i]
        except:
            next = None
            if self:
                previous = self[-1]
            else:
                previous = None
            i = len(self)
            super(ListContainer, self).extend(items)
        else:
            self.data[i:i] = items
            self._p_changed = 1
            previous = None
        self._after_multi_add(items, previous, next, i)

    def reverse(self):
        super(ListContainer, self).reverse()
        self._after_rearrange()

    def sort(self, *args):
        super(ListContainer, self).sort(*args)
        self._after_rearrange()
