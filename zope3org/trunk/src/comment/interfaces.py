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

from zope.interface import Interface
from zope.interface.common.mapping import IEnumerableMapping

from zope.app.annotation.interfaces import IAnnotatable
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.file.interfaces import IFile




class IComment(IFile):
    """Comment."""



class IReadComments(IEnumerableMapping):
    """Read a comments of a comment collection."""



class IAnnotableComments(IAnnotatable):
    """This interface marks components that should provide annotable comments.
    
    Components has to provide a annotations mechanismu."""



class IAttributeAnnotableComments(IAnnotableComments, IAttributeAnnotatable):
    """This interface marks components that should provide attribute annotable comments."""



class IDeleteComments(Interface):
    """Remove a comment from the comment collection."""

    def __delitem__(key):
        """x.__delitem__(key) <==> del x[key]
        
        Declaring this interface does not specify whether __delitem__
        supports slice objects."""



class IAddComments(Interface):
    """Add a comment to the comment collection."""

    def addComment(data, contentType='text/plain'):
        """Create a new comment and add it to the comment collection.

        Return the key of the added comment.
        """



class IEditComments(Interface):
    """Edit a comment of the comment collection."""

    def editComment(key, data, contentType='text/plain'):
        """Edit a comment.

        Change only modified parameters.
        Return a tuple of the changed attributes.
        """



class IComments(IReadComments, IAddComments, IEditComments, IDeleteComments):
    """A collection of comments."""
