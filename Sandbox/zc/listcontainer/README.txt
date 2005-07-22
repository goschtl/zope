-------------
listcontainer
-------------

The listcontainer package is a Zope-3-aware pseudo-list that generates events
upon changes and maintains linked list information on its members.

    >>> from zc import listcontainer
    >>> list1 = listcontainer.ListContainer()
    >>> list1
    []

The listcontainer package is similar in many ways to the zope.app.container
package:

- it resembles a standard Python API (listcontainers resemble lists, and
  zope.app.container objects resemble dicts);

    >>> contained1 = listcontainer.Contained()
    >>> contained1.id = 1 # for sorting below; id is not a requirement
    >>> list1.append(contained1)
    >>> contained2 = listcontainer.Contained()
    >>> contained2.id = 2
    >>> contained3 = listcontainer.Contained()
    >>> contained3.id = 3
    >>> list1.extend([contained3, contained2])
    >>> list1 == [contained1, contained3, contained2]
    True
    >>> len(list1)
    3
    >>> del list1[2]
    >>> list1[1] = contained2
    >>> list1[3:20] = [contained3]
    >>> list1 == [contained1, contained2, contained3]
    True

- contained objects must provide interfaces.IContained, and know about their
  parent and their place within it, a la linked lists;

    >>> list1.append(2)
    Traceback (most recent call last):
    ...
    AssertionError
    >>> contained1.super is contained2.super is contained1.super is list1
    True
    >>> contained1.previous is None
    True
    >>> contained1.next is contained2
    True
    >>> contained2.previous is contained1
    True
    >>> contained2.next is contained3
    True
    >>> contained3.previous is contained2
    True
    >>> contained3.next is None
    True
    >>> list1.pop() is contained3
    True
    >>> contained3.super is None and contained3.previous is None
    True
    >>> contained3.next is None and contained2.next is None
    True
    >>> del list1[0]
    >>> contained1.super is None and contained1.previous is None
    True
    >>> contained1.next is None and contained2.previous is None
    True
    >>> del list1[0:1]
    >>> contained2.super is None
    True
    >>> list1.extend([contained2, contained1])
    >>> list1.insert(0, contained3)
    >>> [contained3, contained2, contained1] == list1
    True
    >>> contained3.super is contained2.super is contained1.super is list1
    True
    >>> contained3.previous is None
    True
    >>> contained3.next is contained2
    True
    >>> contained2.previous is contained3
    True
    >>> contained2.next is contained1
    True
    >>> contained1.previous is contained2
    True
    >>> contained1.next is None
    True

- contained objects may only participate in one listcontainer location at a
  time--they cannot be in multiple listcontainers or be multiple times within
  the same list container (although they may also be in a
  zope.app.container--the packages may be used simultaneously for the same
  object);

    >>> list1.append(contained3)
    Traceback (most recent call last):
    ...
    RuntimeError: Cannot append item that already has a super
    >>> list1[2] = contained3
    Traceback (most recent call last):
    ...
    RuntimeError: Cannot set item that already has a super
    >>> list1.id = 'list1'
    >>> list2 = listcontainer.ListContainer()
    >>> list2.id = 'list2'
    >>> list2.append(contained3)
    Traceback (most recent call last):
    ...
    RuntimeError: Cannot append item that already has a super
    >>> list2[2] = contained3
    Traceback (most recent call last):
    ...
    RuntimeError: Cannot set item that already has a super
    >>> list2.extend([contained3])
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    RuntimeError: ('Cannot add items that already have a super'...
    >>> list1[0:0] = [contained3]
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    RuntimeError: ('Cannot add items that already have a super'...
    >>> list1 == [contained3, contained2, contained1]
    True
    >>> list2 == []
    True

- and listcontainers fire several events to alert subscribers to
  membership changes.  Note that events are generated iff (iff means
  "if and only if") the previous link or the super link have changed
  for a given item.  This means that, for instance, a pop will
  generate a removal event for the item and, if an object follows the
  popped item, a moved event for the following item: the previous link
  has changed.  For example, consider these operations and the events
  they generate.  First we need to set up some ways to look at the
  events that are fired, then we'll actually perform some jobs and
  look at the events.

    >>> from zope import event # ...first setup...
    >>> heard_events = [] # we'll collect the events here
    >>> event.subscribers.append(heard_events.append)
    >>> contained4 = listcontainer.Contained()
    >>> contained4.id = 4
    >>> import pprint
    >>> from zope import interface
    >>> showEventsStart = 0
    >>> def getId(i):
    ...     return i is None and '(none)' or i.id
    ...
    >>> def iname(ob):
    ...     return iter(interface.providedBy(ob)).next().__name__
    >>> def showEvents(start=None): # to generate a friendly view of events
    ...     global showEventsStart
    ...     if start is None:
    ...         start = showEventsStart
    ...     res = [
    ...         ('%s fired for contained%d.' % (iname(ev), ev.object.id),
    ...          '  It was in %s, after %s and before %s' % (
    ...             getId(ev.oldSuper), 
    ...             getId(ev.oldPrevious),
    ...             getId(ev.oldNext)),
    ...          '  It is now in %s, after %s and before %s' % (
    ...             getId(ev.newSuper), 
    ...             getId(ev.newPrevious),
    ...             getId(ev.newNext)))
    ...         for ev in heard_events[start:]]
    ...     res.sort()
    ...     pprint.pprint(res)
    ...     showEventsStart = len(heard_events)
    ...
    >>> list1[0] = contained4 # ...now do something!...
    >>> showEvents()
    [('IObjectAddedEvent fired for contained4.',
      '  It was in (none), after (none) and before (none)',
      '  It is now in list1, after (none) and before 2'),
     ('IObjectReorderedEvent fired for contained2.',
      '  It was in list1, after 3 and before 1',
      '  It is now in list1, after 4 and before 1'),
     ('IObjectReplacedEvent fired for contained3.',
      '  It was in list1, after (none) and before 2',
      '  It is now in (none), after (none) and before (none)')]

  Note that the first of these events, the replaced event, has additional 
  information about what replaced it, duplicating the information in the 
  following add event: 

    >>> ev = heard_events[0]
    >>> ev.replacementOldSuper is None
    True
    >>> ev.replacementOldPrevious is None
    True
    >>> ev.replacementOldNext is None
    True
    >>> ev.replacementNewSuper.id
    'list1'
    >>> ev.replacementNewPrevious is None
    True
    >>> ev.replacementNewNext.id
    2

  Now back to showing some more actions and their associated events.

    >>> list2.append(contained3)
    >>> showEvents()
    [('IObjectAddedEvent fired for contained3.',
      '  It was in (none), after (none) and before (none)',
      '  It is now in list2, after (none) and before (none)')]
    >>> list1.reverse()
    >>> showEvents()
    [('IObjectReorderedEvent fired for contained1.',
      '  It was in list1, after 2 and before (none)',
      '  It is now in list1, after (none) and before 2'),
     ('IObjectReorderedEvent fired for contained2.',
      '  It was in list1, after 4 and before 1',
      '  It is now in list1, after 1 and before 4'),
     ('IObjectReorderedEvent fired for contained4.',
      '  It was in list1, after (none) and before 2',
      '  It is now in list1, after 2 and before (none)')]
    >>> [item.id for item in list1]
    [1, 2, 4]
    >>> list2.pop() is contained3
    True
    >>> showEvents()
    [('IObjectRemovedEvent fired for contained3.',
      '  It was in list2, after (none) and before (none)',
      '  It is now in (none), after (none) and before (none)')]
    >>> list1.insert(0, contained3) # added event, move event
    >>> showEvents()
    [('IObjectAddedEvent fired for contained3.',
      '  It was in (none), after (none) and before (none)',
      '  It is now in list1, after (none) and before 1'),
     ('IObjectReorderedEvent fired for contained1.',
      '  It was in list1, after (none) and before 2',
      '  It is now in list1, after 3 and before 2')]
    >>> list1.sort(lambda a, b: cmp(a.id, b.id)) # three reordered events;
    ... # component2 does not generate a reorder event because it remains after
    ... # component1
    >>> showEvents()
    [('IObjectReorderedEvent fired for contained1.',
      '  It was in list1, after 3 and before 2',
      '  It is now in list1, after (none) and before 2'),
     ('IObjectReorderedEvent fired for contained3.',
      '  It was in list1, after (none) and before 1',
      '  It is now in list1, after 2 and before 4'),
     ('IObjectReorderedEvent fired for contained4.',
      '  It was in list1, after 2 and before (none)',
      '  It is now in list1, after 3 and before (none)')]
    >>> [item.id for item in list1]
    [1, 2, 3, 4]

Listcontainers do not support some aspects of the Python list API.  This is
a complete list of the omissions, to my knowledge:

- inplace multiplication is not allowed since that would usually place
  contained objects multiple times within a listcontainer;

    >>> list1 *= 2
    Traceback (most recent call last):
    ...
    TypeError: does not support in-place multiplication

- as seen above, using standard list manipulation to try and place objects
  already in the same or another listcontainer will fail; and

- while getslice and delslice by step are supported, setslice with step is
  not yet supported.

    >>> [item.id for item in list1[::-1]]
    [4, 3, 2, 1]
    >>> del list1[::2]
    >>> [item.id for item in list1]
    [2, 4]
    >>> list1[::2] = [listcontainer.Contained()]
    Traceback (most recent call last):
    ...
    NotImplementedError

Additionally, unlike usual UserList-based implementations, slices and other
operations that create new sequences do not return the same class, but a
Python list.  This is because, otherwise, it would usually place contained
objects within two listcontainers simultaneously: something not allowed, as
described above.

    >>> type(list1[:])
    <type 'list'>
    >>> out = list1 + [1, 2, 3, contained4]
    >>> out == [contained2, contained4, 1, 2, 3, contained4]
    True
    >>> type(out)
    <type 'list'>
    >>> list2.append(contained3)
    >>> out = list1 + list2
    >>> out == [contained2, contained4, contained3]
    True
    >>> type(out)
    <type 'list'>
    >>> out = list1 * 3
    >>> out == [contained2, contained4, contained2, contained4, contained2, 
    ... contained4]
    True
    >>> type(out)
    <type 'list'>

They also change some list operations (index, remove, count and __contains__)
from operations that compare equality to operations that compare identity.

    >>> class Dummy(listcontainer.Contained):
    ...     def __eq__(self, other):
    ...         return True
    ... 
    >>> d1 = Dummy()
    >>> d1.id = 1
    >>> d2 = Dummy()
    >>> d2.id = 2
    >>> d3 = Dummy()
    >>> d3.id = 3
    >>> l = [d1, d2, d3]
    >>> lc = listcontainer.ListContainer(l)
    >>> d1 == d2 == d3
    True
    >>> l.index(d3) # normal list behavior
    0
    >>> lc.index(d3) # our behavior
    2
    >>> l.remove(d3)
    >>> [d.id for d in l] # normal list behavior
    [2, 3]
    >>> lc.remove(d3) # our behavior
    >>> [d.id for d in lc] # normal list behavior
    [1, 2]
    >>> d4 = Dummy()
    >>> d4.id = 4
    >>> d4 in l
    True
    >>> d4 in lc
    False
    >>> l.count(d1)
    2
    >>> lc.count(d1)
    1
    >>> l.count(d4)
    2
    >>> lc.count(d4)
    0

Listcontainers do support some additional methods to facilitate moves between
one listcontainer and another.  These methods are moveinsert, moveappend,
movereplace, moveextend, and silentpop.  

The four "move*" methods accept items that are already placed in a
listcontainer, unlike the other listcontainer methods.  They move any such
items from the current position and listcontainer to the new position and
listcontainer.  They are also single gesture move operations that
correspondingly fire move events rather than add events when appropriate.

The moveinsert method is similar to the insert method except that it accepts
items already placed in a listcontainer, it accepts multiple items at a 
time, and it will fire move events when appropriate, not merely add events.

    >>> list1.moveinsert(0, contained4, contained1, contained3)
    >>> showEvents(-4)
    [('IObjectAddedEvent fired for contained1.',
      '  It was in (none), after (none) and before (none)',
      '  It is now in list1, after 4 and before 3'),
     ('IObjectMovedEvent fired for contained3.',
      '  It was in list2, after (none) and before (none)',
      '  It is now in list1, after 1 and before 2'),
     ('IObjectReorderedEvent fired for contained2.',
      '  It was in list1, after (none) and before 4',
      '  It is now in list1, after 3 and before (none)'),
     ('IObjectReorderedEvent fired for contained4.',
      '  It was in list1, after 2 and before (none)',
      '  It is now in list1, after (none) and before 1')]
    >>> [item.id for item in list1] # was [2, 4]
    [4, 1, 3, 2]
    >>> list2
    []
    >>> def checkList(l): # define a helper to check list pointers
    ...     previous = None
    ...     for item in l:
    ...         if item.super is not l:
    ...             print "%s super is incorrect: %s" % (
    ...                 item.id, getId(item.super))
    ...             break
    ...         if item.previous is not previous:
    ...             print "%s previous is incorrect: %s" % (
    ...                 item.id, getId(item.previous))
    ...             break
    ...         if previous is not None and previous.next is not item:
    ...             print "%s next is incorrect: %s" % (
    ...                 previous.id, getId(previous.next))
    ...             break
    ...         previous = item
    ...     else:
    ...         if previous is None or previous.next is None:
    ...             print "Correct"
    ...         else:
    ...             print "%s next is incorrect: %s" % (
    ...                 previous.id, getId(previous.next))
    ...
    >>> checkList(list1)
    Correct
    >>> list1.moveinsert(0, contained4) # an expensive noop
    >>> showEvents()
    []
    >>> [item.id for item in list1]
    [4, 1, 3, 2]
    >>> checkList(list1)
    Correct
    >>> list1.moveinsert(0, contained4, contained1) # a more expensive noop
    >>> showEvents()
    []
    >>> [item.id for item in list1]
    [4, 1, 3, 2]
    >>> checkList(list1)
    Correct
    >>> list1.moveinsert(0, contained4, contained1, contained4) # noop
    >>> showEvents()
    []
    >>> [item.id for item in list1]
    [4, 1, 3, 2]
    >>> checkList(list1)
    Correct

The moveappend method is like append except that it accepts items already 
placed in a list container.

    >>> list2.moveappend(contained2)
    >>> showEvents()
    [('IObjectMovedEvent fired for contained2.',
      '  It was in list1, after 3 and before (none)',
      '  It is now in list2, after (none) and before (none)')]
    >>> [item.id for item in list1]
    [4, 1, 3]
    >>> [item.id for item in list2]
    [2]
    >>> checkList(list1)
    Correct
    >>> checkList(list2)
    Correct
    >>> list1.moveappend(contained1)
    >>> showEvents()
    [('IObjectReorderedEvent fired for contained1.',
      '  It was in list1, after 4 and before 3',
      '  It is now in list1, after 3 and before (none)'),
     ('IObjectReorderedEvent fired for contained3.',
      '  It was in list1, after 1 and before (none)',
      '  It is now in list1, after 4 and before 1')]
    >>> [item.id for item in list1]
    [4, 3, 1]
    >>> checkList(list1)
    Correct
    >>> list2.moveappend(contained4)
    >>> showEvents()
    [('IObjectMovedEvent fired for contained4.',
      '  It was in list1, after (none) and before 3',
      '  It is now in list2, after 2 and before (none)'),
     ('IObjectReorderedEvent fired for contained3.',
      '  It was in list1, after 4 and before 1',
      '  It is now in list1, after (none) and before 1')]
    >>> [item.id for item in list1]
    [3, 1]
    >>> [item.id for item in list2]
    [2, 4]
    >>> checkList(list1)
    Correct
    >>> checkList(list2)
    Correct
    >>> list1.moveappend(contained1) # a noop
    >>> showEvents()
    []
    >>> [item.id for item in list1]
    [3, 1]
    >>> checkList(list1)
    Correct

The movereplace method is like a listcontainer setitem operation (e.g.,
list1[0] = contained4), again except that it accepts items already placed in
a list container.

    >>> list2.movereplace(1, contained1)
    >>> showEvents()
    [('IObjectMovedEvent fired for contained1.',
      '  It was in list1, after 3 and before (none)',
      '  It is now in list2, after 2 and before (none)'),
     ('IObjectReplacedEvent fired for contained4.',
      '  It was in list2, after 2 and before (none)',
      '  It is now in (none), after (none) and before (none)')]
    >>> contained4.super is contained4.previous is contained4.next is None
    True
    >>> [item.id for item in list1]
    [3]
    >>> [item.id for item in list2]
    [2, 1]
    >>> checkList(list1)
    Correct
    >>> checkList(list2)
    Correct
    >>> list1.movereplace(1, contained4)
    Traceback (most recent call last):
    ...
    IndexError: list assignment index out of range
    >>> list1.movereplace(0, contained4)
    >>> showEvents()
    [('IObjectAddedEvent fired for contained4.',
      '  It was in (none), after (none) and before (none)',
      '  It is now in list1, after (none) and before (none)'),
     ('IObjectReplacedEvent fired for contained3.',
      '  It was in list1, after (none) and before (none)',
      '  It is now in (none), after (none) and before (none)')]
    >>> contained3.super is contained3.previous is contained3.next is None
    True
    >>> [item.id for item in list1]
    [4]
    >>> [item.id for item in list2]
    [2, 1]
    >>> checkList(list1)
    Correct
    >>> checkList(list2)
    Correct
    >>> list2.movereplace(0, contained2) # noop
    >>> showEvents()
    []
    >>> [item.id for item in list1]
    [4]
    >>> [item.id for item in list2]
    [2, 1]
    >>> checkList(list1)
    Correct
    >>> checkList(list2)
    Correct

Note that this can result in effective insanity: if you tell an object to
replace an object in the same list, and the current position is lower than
the new position, then the resultant index will be the index you specified
minus one.  Note also, in this case, that contained2 did not generate an
event: its container and its previous sibling did not change.  This
conveniently jibes with reality: this operation is an obscure way of spelling
"del list2[1]".

    >>> list2.movereplace(1, contained2) # "move contained2 to position 1"
    >>> showEvents()
    [('IObjectReplacedEvent fired for contained1.',
      '  It was in list2, after 2 and before (none)',
      '  It is now in (none), after (none) and before (none)')]
    >>> contained1.super is contained1.previous is contained1.next is None
    True
    >>> [item.id for item in list1]
    [4]
    >>> [item.id for item in list2] # it is in position 0
    [2]
    >>> checkList(list1)
    Correct
    >>> checkList(list2)
    Correct

The moveextend method is like a listcontainer extend method, with the
now-familiar exception that it accepts items already placed in a list
container.

    >>> list2.moveextend(list1)
    >>> showEvents()
    [('IObjectMovedEvent fired for contained4.',
      '  It was in list1, after (none) and before (none)',
      '  It is now in list2, after 2 and before (none)')]
    >>> [item.id for item in list1]
    []
    >>> [item.id for item in list2]
    [2, 4]
    >>> checkList(list1)
    Correct
    >>> checkList(list2)
    Correct
    >>> list2.moveextend([contained1, contained3])
    >>> showEvents()
    [('IObjectAddedEvent fired for contained1.',
      '  It was in (none), after (none) and before (none)',
      '  It is now in list2, after 4 and before 3'),
     ('IObjectAddedEvent fired for contained3.',
      '  It was in (none), after (none) and before (none)',
      '  It is now in list2, after 1 and before (none)')]
    >>> [item.id for item in list2]
    [2, 4, 1, 3]
    >>> checkList(list2)
    Correct

Seeming insanity again generally ensues if you moveextend items already in
the list.

    >>> list2.moveextend([contained2, contained3, contained4])
    >>> showEvents()
    [('IObjectReorderedEvent fired for contained1.',
      '  It was in list2, after 4 and before 3',
      '  It is now in list2, after (none) and before 2'),
     ('IObjectReorderedEvent fired for contained2.',
      '  It was in list2, after (none) and before 4',
      '  It is now in list2, after 1 and before 3'),
     ('IObjectReorderedEvent fired for contained3.',
      '  It was in list2, after 1 and before (none)',
      '  It is now in list2, after 2 and before 4'),
     ('IObjectReorderedEvent fired for contained4.',
      '  It was in list2, after 2 and before 1',
      '  It is now in list2, after 3 and before (none)')]
    >>> [item.id for item in list2]
    [1, 2, 3, 4]
    >>> checkList(list2)
    Correct

The silentpop method is merely a version of the standard listcontainer pop
that does not fire a removed event (and is thus "silent").  It is used to
support the "move*" operations and is exposed in the interface primarily
because the move operations must rely on it existing on other listcontainers.
It probably should not be used by any other code, as it bypasses the event
system entirely.

    >>> list2.silentpop() is contained4
    True
    >>> showEvents()
    []
    >>> [item.id for item in list2]
    [1, 2, 3]
    >>> checkList(list2)
    Correct
    >>> list2.silentpop(-2) is contained2
    True
    >>> showEvents()
    []
    >>> [item.id for item in list2]
    [1, 3]
    >>> checkList(list2)
    Correct
    >>> list2.silentpop(0) is contained1
    True
    >>> showEvents()
    []
    >>> [item.id for item in list2]
    [3]
    >>> checkList(list2)
    Correct

    >>> event.subscribers.pop() and None # end of test: remove subscriber
