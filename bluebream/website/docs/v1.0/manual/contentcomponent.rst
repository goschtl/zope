Content Component
=================

Introduction
------------

See this example::

  >>> from zope import interface

  >>> class IPerson(interface.Interface):
  ...     name = interface.Attribute("Name")
  >>> class Person(object):
  ...     interface.implements(IPerson)
  ...     name = None
  >>> jack = Person()
  >>> jack.name = "Jack"

Here `jack` is a content component.  So a content component is nothing but an
object which provides a particular interface.  As said in the previous chapter,
use ``zope.schema`` to define fields of interface.  The above interface can be
declared like this::

  >>> from zope import interface
  >>> from zope import schema

  >>> class IPerson(interface.Interface):
  ...     name = schema.TextLine(
  ...         title=u"Name",
  ...         description=u"Name of person",
  ...         default=u"",
  ...         required=True)

If you are developing an enterprise application content will be the most
important thing you have to organize first.  To learn Zope 3 application
development with content components, this chapter introduce a simple
ticket/issue collector application.

First look at the user stories, this book will implement these stories in
coming chapters.

1. Individual small ticket collector for each project.  Many
   collectors can be added to one running zope.

2. Any number of tickets can be added to one collector.

3. Each ticket will be added with a description and one initial
   comment.

4. Additional comments can be added to tickets.

This chapter starts a simple implementation of ticket collector.

As stated above, our goal is to develop a fully functional, though
not great-looking, web-based ticket collector application.  The root
object will be the ``Collector``, which can contain ``Ticket``
objects from various users.  Since you want to allow people to
respond to various tickets, you have to allow tickets to contain
replies, which are ``Comment`` objects.

That means you have two container-based components: The ``Collector``
contains only tickets and can be added to any Folder or container
that wishes to be able to contain it.  To make the ticket collector
more interesting, it also has a description, which briefly introduces
the subject/theme of the discussions hosted.  ``Tickets``, on the
other hand should be only contained by ticket collector.  They will
each have a summary and a description.  And last ``Comment`` should
be only contained by tickets.

This setup should contain all the essential things that you need to
make the object usable.  Later on you will associate a lot of other
meta-data with these components to integrate them even better into
BlueBream and add additional functionality.

The most convenient place to put your package is
``$HOME/myzope/lib/python``.  To create that package, add a directory
using::

  $ cd $HOME/myzope/lib/python/
  $ mkdir collector

on GNU/Linux.

To make this directory a package, place an empty __init__.py file in the new
directory.  In GNU/Linux you can do something like::

  $ echo "# Make it a Python package" >> collector/__init__.py

but you can of course also just use a text editor and save a file of this name.
Just make sure that there is valid Python code in the file.  The file should at
least contain some whitespace, since empty files confuse some archive programs.

From now on you are only going to work inside this ``collector`` package, which
should be located at ``$HOME/myzope/lib/python/collector``.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
