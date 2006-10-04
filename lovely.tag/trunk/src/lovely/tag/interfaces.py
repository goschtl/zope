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
"""Interfaces

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema

class ITag(zope.interface.Interface):
    """A single tag."""

    item = zope.schema.Int(
        title=u'Item',
        description=u'The item that is tagged.',
        required=True)

    user = zope.schema.TextLine(
        title=u'User',
        description=u'The user id that created the tag.',
        required=True)

    name = zope.schema.TextLine(
        title=u'Tag Name',
        description=u'The tag name the user provided for the item.',
        required=True)

    timestamp = zope.schema.Datetime(
        title=u'Timestamp',
        description=u"The timestamp of the tag's creation date",
        required=True)


class ITaggingEngine(zope.interface.Interface):
    """Manangement and Querying of Tags.

    Tags are small stickers that are specific to an object to be tageed and
    the user tagging the object.
    """

    def update(item, user, tags):
        """Update the tagging engine for an item and user and its tags.

        The item must be an integer, the user can be a string and the tags
        argument must be an iterable of tag names (strings).

        This method always overwrites the old tag settings. However, existing
        tags will not be readded and are just skipped.
        """

    def getTags(items=None, users=None):
        """Get all tags matching the specified items and users.

        If no items are specified, match all items. Ditto for users.

        The method returns a set of *normalized* tag names.
        """

    def getItems(tags=None, users=None):
        """Get all items matching the specified items and users.

        If no tags are specified, match all tags. Ditto for users.

        The method returns a set of item ids.
        """

    def getUsers(tags=None, items=None):
        """Get all items matching the specified tags and items.

        If no tags are specified, match all tags. Ditto for items.

        The method returns a set of user strings.
        """

    def getRelatedTags(tag, degree=1):
        """Get a set of all related tags."""

    def getCloud(item=None, user=None):
        """Get a set of tuples in the form of ('tag', frequency)."""

    def getFrequency(tags):
        """Get the frequency of all tags

        Returns tuples in the form of ('tag', frequency)
        """


class ITaggable(zope.interface.Interface):
    """A marker interface to declare an object as being able to be tagged."""


class ITagging(zope.interface.Interface):
    """Provides a tagging API for a single item.

    Effectively, this interface provides a simplification (special case) of
    the tagging engine API.
    """

    def update(user, tags):
        """Update the tags of an item.

        See ``ITaggingEngine.update()`` for more information.
        """

    def getTags(users=None):
        """Get all tags matching the specified users.

        See ``ITaggingEngine.getTags()`` for more information.
        """

    def getUsers(tags=None):
        """Get all items matching the specified tags.

        See ``ITaggingEngine.getUsers()`` for more information.
        """

class IUserTagging(zope.interface.Interface):

    """Provides easy tagging of objects based on the current
    principal"""

    tags = zope.schema.Set(title=u'Tags',
                           description=u'Tags for the current User',
                           required=False)


class ITagIndex(zope.interface.Interface):

    def apply(query):
        """Return None or an IFTreeSet of the doc ids that match the query.

        query is a dict with one of the following keys: and, or

        Any one of the keys may be used; using more than one is not allowed.

        'any_of' : docs containing at least one of the keys are returned. The
                   value is a list containing the tags.
        'all_of' : docs containing at alll of the tags are returned. The value
                   is a list containing the tags.
        """
