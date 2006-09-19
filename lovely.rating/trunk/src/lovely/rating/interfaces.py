##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Rating interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

from schooltool.requirement import interfaces

class IRatingDefinition(zope.interface.Interface):
    """Defines the a rating.

    The purpose of this interface is to specify the purpose of the rating (or
    what is being rated) and the way it is rated, in other words, the score
    system.
    """

    title = zope.schema.TextLine(
        title=u'Title',
        description=u'The title of the rating survey.',
        required=True)

    scoreSystem = zope.schema.Object(
        title=u'Score System',
        description=u'The score system used for rating.',
        schema=interfaces.IScoreSystem,
        required=True)

    description = zope.schema.Text(
        title=u'Description',
        description=u'A longer explanation of the purpose of the survey.',
        required=False)


class IRatable(zope.interface.Interface):
    """A marker interface marking an object as being ratable."""


class IRatingsManager(zope.interface.Interface):
    """Manages all ratings for one object."""

    def rate(id, value, user):
        """Create a rating for the definition with 'id'.

        This method should override existing ratings, if applicable.
        """

    def remove(id, user):
        """Remove the rating for the definition and user.

        If no rating exists, do nothing and simply return.
        """

    def getRatings(id):
        """Get all ratings for a particular definition.

        The result will be a sequence of ``IRating`` objects.
        """

    def getRating(id, user):
        """Get a rating for the definition and user.

        The result will be an ``IRating`` object. If no rating is found, rais
        a ``ValueError``.
        """

    def computeAverage(id):
        """Compute the average rating value for the specified definition."""

    def countScores(id):
        """Count how many times each value was giving for a definition.

        The result will be a list of tuples of the type ``(score,
        amount)``. ``score`` is in turn a tuple of ``(name, value)``.
        """
        
    def countAmountRatings(id):
        """Counts the total amount of ratings for one definition"""


class IRating(zope.interface.Interface):
    """A single rating for a definition and user."""

    value = zope.schema.Object(
        title=u'Value',
        description=u'A scoresystem-valid score that represents the rating.',
        schema=zope.interface.Interface,
        required=True)

    user = zope.schema.TextLine(
        title=u'User',
        description=u'The id of the entity having made the rating.',
        required=True)

    timestamp = zope.schema.Datetime(
        title=u'Timestamp',
        description=u'The time the rating was given.')
