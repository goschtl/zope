========
Comments
========

This package can be used to comment components. The provided functionality relies
on the annotations mechanism. We implement a subject that we are going to
comment afterward:

    >>> from zope.app.container.contained import Contained
    >>> from zope.interface import implements
    >>> from comment import IAttributeAnnotableComments

    >>> class Subject(Contained):
    ...     implements(IAttributeAnnotableComments)
    ...     pass

    >>> subject = Subject()

The comment annotated comments can be retrieved by an adaption to IComments:

    >>> from comment import IComments

    >>> comments = IComments(subject)

Per default no comments are stored within comments:

    >>> len(comments)
    0

You can add a few comments. If no content type is defined `text/plain` is
assumed as default:

    >>> comments.addComment('foo')
    >>> comments.addComment('<bar />', 'text/xml')
    >>> comments.addComment('<html />', 'text/html')

    >>> len(comments)
    3

You can iterate over the comments:

    >>> for comment in comments:
    ...     print comment.data, comment.contentType
    foo text/plain
    <bar /> text/xml
    <html /> text/html

You can delete comment passing its index:

    >>> del comments[1]
    >>> len(comments)
    2
    
    >>> for comment in comments:
    ...     print comment.data, comment.contentType
    foo text/plain
    <html /> text/html

    



                         

