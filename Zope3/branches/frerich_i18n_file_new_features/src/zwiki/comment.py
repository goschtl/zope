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
"""WikiPage Comment

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent

from zope.interface import implements
from zope.schema.vocabulary import getVocabularyRegistry
from zope.app.container.contained import Contained
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app.filerepresentation.interfaces import IReadFile, IWriteFile

from zwiki.interfaces import IComment
from zwiki.interfaces import IWikiPageContained


class Comment(Persistent, Contained):
    r"""A simple persistent comment implementation.

    The comment is really a primitive object, since it only declares a couple
    of attributes. The only thing interesting here is the title, which
    retrieved from its Dublin Core value.

    First off let's make sure that we actually implement the interface:

      >>> comment = Comment()
      >>> IComment.providedBy(comment)
      True

    Now, verify that the attributes are set correctly.

      >>> comment.source
      u''
      >>> comment.source = u'comment 1'
      >>> comment.source
      u'comment 1'

      >>> comment.type
      u'zope.source.rest'
      >>> comment.type = u'zope.source.stx'
      >>> comment.type
      u'zope.source.stx'

      >>> comment.title
      u''
      >>> comment.title = u'C1'
      >>> comment.title
      u'C1'

    (Note: The comment is not responsible for checking the validity of the
    type.)    
    
    """
    implements(IComment, IWikiPageContained)
    
    # See wiki.interfaces.IComment
    source = u''
    
    # See wiki.interfaces.IComment
    type = u'zope.source.rest'

    # See wiki.interfaces.IComment
    def _getTitle(self):
        dc = ICMFDublinCore(self)
        return dc.title

    def _setTitle(self, title):
        dc = ICMFDublinCore(self)
        dc.title = title

    title = property(_getTitle, _setTitle)


# Adapters for file-system style access

class CommentFile:
    r"""Adapter for letting a Comment look like a regular readable file.

    Example of Usage:

      >>> comment = Comment()
      >>> comment.title = u'Comment 1'
      >>> comment.source = u'This is a comment'
      >>> file = CommentFile(comment)

    Now let's see whether we can read the comment file.

      >>> file.read()
      u'Title: Comment 1\nType: zope.source.rest\n\nThis is a comment'

    And that the size of the file is correct:

      >>> file.size()
      58

    Let's see whether we can also write to a file correctly:

      >>> file.write('Title: C1\nType: zope.source.stx\n\ncomment 1')
      >>> comment.title
      u'C1'
      >>> comment.type
      u'zope.source.stx'
      >>> comment.source
      u'comment 1'

    Sometimes the user might not have entered a valid type; let's ignore the
    assignment then.

      >>> file.write('Type: zope.source.foo\n\ncomment 2')
      >>> comment.title
      u'C1'
      >>> comment.type
      u'zope.source.stx'
      >>> comment.source
      u'comment 2'

    In the previous example the title was missing, but the type is optional
    too:

      >>> file.write('Title: C3\n\ncomment 3')
      >>> comment.title
      u'C3'
      >>> comment.type
      u'zope.source.stx'
      >>> comment.source
      u'comment 3'
    """

    implements(IReadFile, IWriteFile)
    __used_for__ = IComment

    def __init__(self, context):
        self.context = context

    def read(self):
        """See zope.app.filerepresentation.interfaces.IReadFile"""
        text = 'Title: %s\n' %self.context.title
        text += 'Type: %s\n\n' %self.context.type
        text += self.context.source
        return text

    def size(self):
        """See zope.app.filerepresentation.interfaces.IReadFile"""
        return len(self.read())

    def write(self, data):
        """See zope.app.filerepresentation.interfaces.IWriteFile"""
        if data.startswith('Title: '):
            title, data = data.split('\n', 1)
            self.context.title = unicode(title[7:])

        if data.startswith('Type: '):
            type, data = data.split('\n', 1)
            type = type[6:]
            vocab = getVocabularyRegistry().get(self.context, 'SourceTypes')
            if type in [term.value for term in vocab]:
                self.context.type = unicode(type)

        if data.startswith('\n'):
            data = data[1:]

        self.context.source = unicode(data)


class CommentFileFactory(object):
    r"""A factory that creates a comment.

    This component is used by the WikiPage file representation. If you add a
    file to a wiki page, then it is interpreted as adding a comment to the
    wiki page.

    Usage:

      >>> factory = CommentFileFactory(None)
      >>> comment = factory('foo' ,'',
      ...                   'Title: C1\nType: zope.source.stx\n\nComment 1')
      >>> comment.title
      u'C1'
      >>> comment.type
      u'zope.source.stx'
      >>> comment.source
      u'Comment 1'
    """

    def __init__(self, context):
        """Initialize the object."""

    def __call__(self, name, content_type, data):
        """The comment is created from the provided information."""
        comment = Comment()
        CommentFile(comment).write(data)
        return comment
