========
Comments
========

The comment package is a simple way to add comments to any ``IAnnotatable``
Zope content.  The datetime and current principals are stamped on to the
comment.  The comment body is currently simply unicode text but intended to be
html snippets ("rich text") at a later date.

The inclusion of current principals requires an interaction, which is what we
need to set up before we can use the system here.  Below, we set up a dummy
interaction with dummy participants, create some content that is
``IAttributeAnnotatable``, and then finally show the system in use.

In order to create a participation, we need a few principals:

    >>> import zope.security.management
    >>> import zope.security.interfaces
    >>> from zope import interface
    >>> class Principal(object):
    ...     interface.implements(zope.security.interfaces.IPrincipal)
    ...
    ...     def __init__(self, id, title, description):
    ...         self.id = id
    ...         self.title = title
    ...         self.description = description
    ...
    ...     def __repr__(self):
    ...         return '<%s %r>' %(self.__class__.__name__, self.id)

    >>> alice = Principal('alice', 'Alice Aal', 'first principal')
    >>> betty = Principal('betty', 'Betty Barnes', 'second principal')

Now we can create a participation:

    >>> class Participation(object):
    ...     zope.interface.implements(
    ...         zope.security.interfaces.IParticipation,
    ...         zope.publisher.interfaces.IRequest)
    ...     interaction = principal = None
    ...
    ...     def __init__(self, principal):
    ...         self.principal = principal
    ...
    ...     def __repr__(self):
    ...         return '<%s %r>' %(self.__class__.__name__, self.principal)

Next we need to make sute the annotation mechanism is setup, because the
comments adapter needs to be able to annotate the adapted object:

    >>> import zope.component
    >>> import zope.annotation
    >>> zope.component.provideAdapter(
    ...     zope.annotation.attribute.AttributeAnnotations)

Let's now make sure that all commentable objects can receive comments:

    >>> from zc.comment import comment
    >>> zope.component.provideAdapter(comment.CommentsFactory)

Now that we have everything setup, let's have a look at how it works. First we
need a simple content component:

    >>> class SimpleContent(object):
    ...     interface.implements(
    ...         zope.annotation.interfaces.IAttributeAnnotatable)
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return '<%s %r>' %(self.__class__.__name__, self.name)
    >>> content = SimpleContent(u'content')

In order to play with the comments, we now have to register a new
participation. In our case, Alice wants to create a comment:

    >>> zope.security.management.endInteraction()
    >>> zope.security.management.newInteraction(Participation(alice))

We can access the comments of an object by adapting to ``IComments``:

    >>> from zc.comment import interfaces
    >>> comments = interfaces.IComments(content)
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt',
                <SimpleContent u'content'>,
                <InterfaceClass zc.comment.interfaces.IComments>)

Initially, the component is not commentable, because it does not provide the
correct interface:

    >>> zope.interface.directlyProvides(content, interfaces.ICommentable)

    >>> comments = interfaces.IComments(content)
    >>> comments
    <Comments (0) for <SimpleContent u'content'>>

Let's now add a comment:

    >>> import datetime, pytz
    >>> before = datetime.datetime.now(pytz.utc)

    >>> comments.add(u"Foo!  Bar!")

    >>> after = datetime.datetime.now(pytz.utc)

As you can see it was not necessary to create the comments object manually,
but simply pass in the text. Clearly a comment has been added:

    >>> len(comments)
    1

Let's now make sure that the data was set correctly:

    >>> comments[0].body
    u'Foo!  Bar!'
    >>> before <= comments[0].date <= after
    True
    >>> comments[0].principal_ids
    ('alice',)

Let's now log in as Betty:

    >>> zope.security.management.endInteraction()
    >>> zope.security.management.newInteraction(Participation(betty))

Betty can also add a comment:

    >>> comments = interfaces.IComments(content)
    >>> before = datetime.datetime.now(pytz.utc)
    >>> comments.add(u"Shazam")
    >>> after = datetime.datetime.now(pytz.utc)
    >>> len(comments)
    2

And her comment is also correctly stored:

    >>> comments[1].body
    u'Shazam'
    >>> before <= comments[1].date <= after
    True
    >>> comments[1].principal_ids
    ('betty',)

Let's now make sure that if multiple participants are in the interaction that
all of them get picked up:

    >>> zope.security.management.endInteraction()
    >>> zope.security.management.newInteraction(
    ...     Participation(alice), Participation(betty))

    >>> comments.add(u"Boom.")
    >>> len(comments)
    3
    >>> comments[2].body
    u'Boom.'
    >>> comments[2].principal_ids
    ('alice', 'betty')

Finally, note that we can only add unicode text as a valid comment:

    >>> comments.add(42)
    Traceback (most recent call last):
    ...
    WrongType: (42, <type 'unicode'>, 'body')

If you like, you can always clear all comments:

    >>> comments.clear()
    >>> len(comments)
    0

And of course some cleanup:

    >>> zope.security.management.endInteraction()
