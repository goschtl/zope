==============
Rating Package
==============

The rating package implements a rating system which can be plugged to any
content type.

  >>> from lovely.rating import IRatable
  >>> from lovely.rating import IRatingsManager
  >>> from lovely.rating import IRatingDefinition
  >>> from lovely import rating

Let's first create an object that can be rated:

  >>> import zope.annotation
  >>> import zope.interface

  >>> from lovely.rating.interfaces import (IRatable,
  ...                                       IRatingsManager,
  ...                                       IRatingDefinition)
  >>> class Application(object):
  ...     zope.interface.implements(zope.annotation.IAttributeAnnotatable,
  ...                               IRatable)
  ...     def __init__(self, name):
  ...         self.name = name
  ...
  ...     def __repr__(self):
  ...         return '<%s %r>' % (self.__class__.__name__, self.name)

  >>> kde = Application(u'KDE')

In order for an object to be ratable, it also must be annotatable. The easiest
is to make it attribute-annotatble. Now we register an adapter that can adapt
``IRatable`` providing objects to ``IRatingsManagers``.

  >>> import zope.component
  >>> zope.component.provideAdapter(rating.getRatingsManager)

  >>> from zope.annotation import attribute
  >>> zope.component.provideAdapter(attribute.AttributeAnnotations)


It is now trivial to get the ratings manager.

  >>> manager = IRatingsManager(kde)
  >>> manager
  <RatingsManager for <Application u'KDE'>>

The ratings manager manages all ratings that can be made for an object. For
example, you might want to be able to rate an application for usability,
functionality, stability and documentation. The rating manager would then
manage the ratings of those four points of interest.

Before we can rate the application, we have to create a rating definition for
each of the four points of interest. To do this, we first have to
create a score system for the ratings:

  >>> from decimal import Decimal
  >>> from lovely.rating import scoresystem

  >>> fiveSteps = scoresystem.SimpleScoreSystem(
  ...    'fiveSteps', u'Five Steps', u' A five step scoring system',
  ...    [(u'Awesome', Decimal(4)), (u'Good', Decimal(3)),
  ...     (u'Okay', Decimal(2)), (u'Poor', Decimal(1)),
  ...     (u'Crap', Decimal(0))])

Now we can create the rating definition and register it as a utility:

  >>> usability = rating.RatingDefinition(
  ...     u'Usability', fiveSteps, u'How is the usability of the application?')
  >>> zope.component.provideUtility(
  ...     usability, IRatingDefinition, name='usability')

We are finally ready to rate KDE for usability, note that the rate
method returns True if a change occured:

  >>> manager.rate('usability', u'Okay', u'srichter')
  True
  >>> manager.rate('usability', u'Okay', u'kartnaller')
  True

The ``rate()`` method's arguments are the id of the rating definition, the
value and the user id of the user making the rating. Note that you cannot add
invalid ratings:

  >>> manager.rate('usability', u'Divine', u'jodok')
  Traceback (most recent call last):
  ...
  ValueError: Invalid rating value u'Divine' for 'usability'.

  >>> manager.rate('stability', u'Awesome', u'jodok')
  Traceback (most recent call last):
  ...
  ValueError: No rating definition named 'stability' found.

The rest of the rating manager API deals with retrieving the ratings. First
you can ask for all ratings made for a rating definition:

  >>> sorted([rating.__repr__() for rating in manager.getRatings('usability')])
  ["<Rating u'Okay' by u'kartnaller'>", "<Rating u'Okay' by u'srichter'>"]

The getRatings method supports filtering the ratings by timestamp.

  >>> from datetime import datetime, timedelta
  >>> from pytz import UTC
  >>> now = datetime.now(UTC)
  >>> oneDay = timedelta(days=1)

Since we have created all ratings in this test all should be within
this day and before now.

  >>> ratings = manager.getRatings('usability', dtMax=now, dtMin=now-oneDay)
  >>> len(sorted(ratings))
  2

The same result for an undefined dtMax or dtMin.

  >>> ratings = manager.getRatings('usability', dtMin=now-oneDay)
  >>> len(sorted(ratings))
  2
  >>> ratings = manager.getRatings('usability', dtMax=now)
  >>> len(sorted(ratings))
  2

Let us set a timestamp on a rating just for testing (Note, this is
private API)

  >>> r = manager.getRatings('usability', dtMax=now)[0]
  >>> r
  <Rating u'Okay' by u'kartnaller'>
  >>> r._timestamp = r._timestamp - oneDay
  >>> twoDays = timedelta(days=2)
  >>> threeHours = timedelta(hours=3)

Get all ratings that are at most 3 hours old.

  >>> ratings = manager.getRatings('usability', dtMin=now-threeHours)
  >>> sorted(ratings)
  [<Rating u'Okay' by u'srichter'>]
  
Get all ratings that are at least 3 hours old.

  >>> ratings = manager.getRatings('usability', dtMax=now-threeHours)
  >>> sorted(ratings)
  [<Rating u'Okay' by u'kartnaller'>] 

Get all ratings from the last two days.

  >>> ratings = manager.getRatings('usability', dtMin=now-twoDays)
  >>> sorted(ratings)
  [<Rating u'Okay' by u'kartnaller'>, <Rating u'Okay' by u'srichter'>]

You can also ask for the rating of a particular user:

  >>> manager.getRating('usability', u'srichter')
  <Rating u'Okay' by u'srichter'>

The rating has the following attributes:

  >>> manager.getRating('usability', u'srichter').value
  u'Okay'
  >>> manager.getRating('usability', u'srichter').user
  u'srichter'
  >>> ts = manager.getRating('usability', u'srichter').timestamp
  >>> ts
  datetime.datetime(..., tzinfo=<UTC>)

Note that if a user rates an object with the same value again the
timestamp is not changed.

  >>> manager.rate('usability', u'Okay', u'srichter')
  False
  >>> ts == manager.getRating('usability', u'srichter').timestamp
  True

But if the value changes the timestamp is updated.

  >>> manager.rate('usability', u'Good', u'srichter')
  True
  >>> ts == manager.getRating('usability', u'srichter').timestamp
  False

Note that the rating object is read-only:

  >>> manager.getRating('usability', u'srichter').value = u'Awesome'
  Traceback (most recent call last):
  ...
  AttributeError: can't set attribute

A new rating can be given by rating the application again:

  >>> manager.rate('usability', u'Awesome', u'srichter')
  True
  >>> manager.getRating('usability', u'srichter')
  <Rating u'Awesome' by u'srichter'>

Ratings are removed using the following. This method also returns a
boolean indicating if something has changed.:

  >>> manager.rate('usability', u'Crap', u'badcarma')
  True
  >>> manager.getRating('usability', u'badcarma')
  <Rating u'Crap' by u'badcarma'>

  >>> manager.remove('usability', 'badcarma')
  True
  >>> manager.remove('usability', 'badcarma')
  False
  >>> manager.getRating('usability', u'badcarma')

Finally, the manager also provides some basic statistical features:

  >>> manager.computeAverage('usability')
  Decimal("3")

  >>> manager.countScores('usability')
  [((u'Awesome', Decimal("4")), 1),
   ((u'Good', Decimal("3")), 0),
   ((u'Okay', Decimal("2")), 1),
   ((u'Poor', Decimal("1")), 0),
   ((u'Crap', Decimal("0")), 0)]

The computeAverage, countScores and countAmountRatings methods also
support the dtMin and dtMax arguments as described in the getRatings
method.
