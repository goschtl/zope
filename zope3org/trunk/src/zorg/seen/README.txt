====
Seen
====

This package can be used to mark components as seen or unseen. 
The provided functionality relies on the annotations mechanism. 
We implement a subject that we are going to mark afterward:

    >>> from zope.app.container.contained import Contained
    >>> from zope.interface import implements
    >>> from zope.app.annotation.interfaces import IAttributeAnnotatable
    >>> from zorg.seen.interfaces import ISeeableAttributeAnnotable

    >>> class Subject(Contained):
    ...     implements(ISeeableAttributeAnnotable)
    ...     pass

    >>> subject = Subject()

The datetimes at whcih the user marked the subject can be retrieved 
by an adaption to ISeen:

    >>> from zorg.seen.interfaces import ISeen
    >>> seen = ISeen(subject)

The seen marks can be read using the regular IEnumerableMapping.
At the moment no marks are stored within seen:

    >>> seen['zorg.member.uwe']
    Traceback (most recent call last):
    ...
    KeyError: 'zorg.member.uwe'

    >>> seen.get('zorg.member.uwe')

    >>> 'zorg.member.uwe' in seen
    False

    >>> seen.keys()
    []

    >>> [i for i in seen]
    []

    >>> seen.values()
    []

    >>> seen.items()
    []

    >>> len(seen)
    0

You can mark the subject as seen. The addition notifies a modification event
for the marked object:

    >>> seen.markAsSeen('zorg.member.uwe')
    'zorg.member.uwe'

    >>> from zope.app.event.tests.placelesssetup import events, clearEvents
    >>> len(events)
    1

    >>> e = events.pop()
    >>> (e.object == subject, e.__class__.__name__ , 
    ...  e.descriptions[0].interface.__name__, e.descriptions[0].keys)
    (True, 'ObjectModifiedEvent', 'ISeen', ('zorg.member.uwe',))


We add a few more marks...:

    >>> seen.markAsSeen('zorg.member.dominik')
    'zorg.member.dominik'
    >>> seen.markAsSeen('zorg.member.gregoire')
    'zorg.member.gregoire'

... and check the read methods:

    >>> seen['zorg.member.dominik'] # doctest: +ELLIPSIS
    datetime.datetime...

    >>> seen.get('zorg.member.dominik') == seen['zorg.member.dominik']
    True

    >>> 'zorg.member.gregoire' in seen
    True

    >>> pprint(sorted(seen.keys()))
    ['zorg.member.dominik',
     'zorg.member.gregoire',
     'zorg.member.uwe']
     
    >>> pprint(sorted([i for i in seen]))
    ['zorg.member.dominik',
     'zorg.member.gregoire',
     'zorg.member.uwe']

    >>> pprint(seen.items()) # doctest: +ELLIPSIS
    [('zorg.member.dominik',
      datetime.datetime(..., tzinfo=<UTC>)),
     ('zorg.member.uwe',
      datetime.datetime(..., tzinfo=<UTC>)),
     ('zorg.member.gregoire',
      datetime.datetime(..., tzinfo=<UTC>))]

    >>> len(seen)
    3

You can iterate over the marks:

    >>> for mark in seen.values():
    ...     print mark.__class__.__name__
    datetime
    datetime
    datetime

You can delete a mark passing its key. The deletion notifies
an object modified event for the context:

    >>> clearEvents()

    >>> del seen['zorg.member.dominik']
    >>> len(seen)
    2

    >>> len(events)
    1

    >>> e = events.pop()
    >>> (e.object == subject, e.__class__.__name__ , 
    ...  e.descriptions[0].interface.__name__, e.descriptions[0].attributes)
    (True, 'ObjectModifiedEvent', 'ISeen', ())

Alternatively you can use the synonymous markAsUnseen method :

    >>> seen.markAsUnseen('zorg.member.uwe')
    >>> len(seen)
    1
