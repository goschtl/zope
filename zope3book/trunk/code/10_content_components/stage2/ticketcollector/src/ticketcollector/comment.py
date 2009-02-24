from zope.interface import implements

from interfaces import IComment
from interfaces import ICommentContained
from zope.app.container.contained import Contained

class Comment(Contained):
    """A simple implementation of a comment.

    Make sure that the ``Comment`` implements the ``IComment`` interface::

      >>> from zope.interface.verify import verifyClass
      >>> verifyClass(IComment, Comment)
      True

    Here is an example of changing the body of the comment::

      >>> comment = Comment()
      >>> comment.body
      u''
      >>> comment.body = u'Comment Body'
      >>> comment.body
      u'Comment Body'
    """

    implements(IComment, ICommentContained)

    body = u""
