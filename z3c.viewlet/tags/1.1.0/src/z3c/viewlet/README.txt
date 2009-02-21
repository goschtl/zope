==================
Viewlet Extensions
==================

This package provides extensions to the basic ``zope.viewlet`` package
functionality.


Weight-Ordered Viewlet Manager
------------------------------

The viewlet manager in ``zope.viewlet`` does not implement a particular way of
sorting the viewlets it represents. This was intentional, since the authors
did not want to suggest a particular method of sorting viewlets. Over time,
however, it turns out that sorting viewlets by a relative weight is very
useful and sufficient for most situations.

  >>> from z3c.viewlet import manager

Every viewlet displayed by a weight-ordered viewlet manager is expected to
have a ``weight`` attribute that is an integer; it can also be a string that
can be converted to an integer. If a viewlet does not have this attribute, a
weight of zero is assumed.

The manager uses a helper function to extract the weight. So let's create a
dummy viewlet:

  >>> class Viewlet(object):
  ...   pass

  >>> viewlet = Viewlet()

Initially, there is no weight attribute, so the weight is zero.

  >>> manager.getWeight(('viewlet', viewlet))
  0

If the viewlet has a weight, ...

  >>> viewlet.weight = 1

... it is returned:

  >>> manager.getWeight(('viewlet', viewlet))
  1

As mentioned before, the weight can also be a string representation of an
integer:

  >>> viewlet.weight = '2'
  >>> manager.getWeight(('viewlet', viewlet))
  2

Let's now check that the sorting works correctly for the manager:

  >>> zero = Viewlet()

  >>> one = Viewlet()
  >>> one.weight = 1

  >>> two = Viewlet()
  >>> two.weight = '2'

  >>> viewlets = manager.WeightOrderedViewletManager(None, None, None)
  >>> viewlets.sort([ ('zero', zero), ('one', one), ('two', two) ])
  [('zero', <Viewlet object at ...>),
   ('one', <Viewlet object at ...>),
   ('two', <Viewlet object at ...>)]
