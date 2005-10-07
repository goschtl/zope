##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""

$Id$
"""

import persistent.list
import zope.component
import zope.interface
import zope.app
import zope.app.annotation

from zope.app.annotation.interfaces import IAnnotations
from zope.app.file import File
from zope.app.location import Location

from comment import IAnnotableComments
from comment import IComment
from comment import IComments

commentsKey = 'comment.comments'



def dottedName(klass):
    if klass is None:
        return 'None'
    return klass.__module__ + '.' + klass.__name__



class Comment(File):
    """Comment implementation."""

    zope.interface.implements(IComment)



class CommentsForAnnotatable(Location):
    """Annotate comments."""

    zope.component.adapts(IAnnotableComments,)
    zope.interface.implements(IComments)

    def __init__(self, context):
        self.context = context

    # private methods
    def _get__annotations(self):
        annotations = self.__dict__.get('_annotations')
        
        if annotations is None:
            self.__dict__['_annotations']= annotations = IAnnotations(self.context)
        
        return annotations

    _annotations = property(_get__annotations)

    # public methods
    def addComment(self, data, contentType='text/plain'):
        """See comment.IAddComments"""
        comment = Comment(data, contentType)

        annot = self._annotations
        annot[commentsKey] = annot.get(commentsKey, ()) + (comment,)

    def __delitem__(self, index):
        """See comment.IDeleteComments"""
        annot = self._annotations
        comments = annot.get(commentsKey, ())
        annot[commentsKey] = tuple([comments[i] for i in range(len(comments)) if i != index])

    def __getitem__(self, index):
        """See zope.interface.common.sequence.IFiniteSequence"""
        annot = self._annotations
        return annot.get(commentsKey, ())[index]
        
    def __iter__(self):
        """See zope.interface.common.sequence.IFiniteSequence"""
        annot = self._annotations
        return iter(annot.get(commentsKey, ()))

    def __len__(self):
        """See zope.interface.common.sequence.IFiniteSequence"""
        annot = self._annotations
        return len(annot.get(commentsKey, ()))
