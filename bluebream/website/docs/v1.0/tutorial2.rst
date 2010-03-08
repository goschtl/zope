.. _tut2-tutorial:

Tutorial --- Part 2
===================

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

.. _tut2-intro:

Introduction
------------

This is the second part of tutorial.  In the first part, you learned
about project directory structure, Buildout configuration, content
components and using the form library.  Content components are
objects with a user visisble view.  A view could be a browser view
(HTML/JS/CSS) or JSON or XMLRPC or any other view.  To exaplain the
idea of content components, the ticket collector project started in
the first part of tutorial will be expanded with additional
functionalities.  In fact, the collector object created in the last
chapter is a content component.  In this chapter, you will create new
content objects like tickets and comments.  Another thing you might
be noticed that every content component, including container objects,
there is well defined interface defined using ``zope.interface``
module.

This chapter explore content components in more detail.  After
completing this chapter, you should be able to:

- Define schema for content components
- Create container objects
- Use ZCML to configure various components

Before proceeding further, here is an overview of sections:

- **Adding tickets** -- This section shows creating a ticket
  collector objects.  This section provide a detailed overview of
  creating content object and demonstrate with a simple example.

- **Adding comments** -- This section explain about adding content
  object inside other container objects.  Ticket objects will be
  transformed to a container object.

.. _tut2-adding-tickets:

Adding tickets
--------------

Schema definition
~~~~~~~~~~~~~~~~~

In this section, you will learn about adding tickets to collector.
In order to use ticket objects, first you need to create an interface
for tickets.  Update the ``src/tc/main/interfaces.py`` with the ticket
interface::

  class ITicket(Interface):
     """Ticket - the main content component"""

      name = TextLine(
          title=u"Name",
          description=u"Name of application.",
          default=u"",
          required=True)

      summary = Text(
          title=u"Summary",
          description=u"Ticket summary",
          default=u"",
          required=True)

The ``Interface``, ``TextLine`` and ``Text`` are already imported, if
not, you can import it from these locations::

  from zope.container.interfaces import IContainer
  from zope.schema import TextLine
  from zope.schema import Text

It would be good if you set a precondition to restrict what types of
objects you want to add inside a collector.  Now you know that, you
only expect tickets objects inside collector.  So, you can add a
precondition for restricting only ticket objects inside collector.
To do this, you need to add a ``__setitem__`` method to
``ICollector`` interface definition (The ``__setitem__`` is part of
``IContainer`` API).  Then below that, you can add ``precondition``
attribute, which is an instance of ``ItemTypePrecondition`` class.
You can pass the interfaces as arguments to ``ItemTypePrecondition``
class.  Below, only one class (``ITicket``) is passed.  So, only
ticket objects are allowed inside collector.

::

    from zope.app.container.constraints import ItemTypePrecondition

    def __setitem__(name, object):
        """Add an ICollector object."""

    __setitem__.precondition = ItemTypePrecondition(ITicket)

The ``ItemTypePrecondition`` provides a way to restrict the type of
object which can be added inside a container.  You can also specify
that ticket objects can be only added inside collector.  To do this,
you need to create another interface inheriting from
``zope.container.interfaces.IContained``.

::

  from zope.schema import Field
  from zope.container.interfaces import IContained
  from zope.app.container.constraints import ContainerTypesConstraint

  class ITicketContained(IContained):
      """Interface that specifies the type of objects that can contain
      tickets.  So a ticket can only contain in a collector."""

      __parent__ = Field(
          constraint = ContainerTypesConstraint(ICollector))

Here you added a constraint for ``__parent__`` field using
``ContainerTypesConstraint`` class.

Implementation
~~~~~~~~~~~~~~

Next, you can implement this interface inside ``ticket.py``::

  from zope.interface import implements
  from tc.main.interfaces import ITicket
  from tc.main.interfaces import ITicketContained
  from zope.location.contained import Contained


  class Ticket(Contained):

      implements(ITicket, ITicketContained)

      number = u""
      summary = u""

Configuration
~~~~~~~~~~~~~

Then, register the interface & class::

  <interface 
     interface=".interfaces.ITicket" 
     type="zope.app.content.interfaces.IContentType"
     /> 

  <class class=".ticket.Ticket">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <require
       permission="zope.ManageContent"
       interface=".interfaces.ITicket"
       />
    <require
       permission="zope.ManageContent"
       set_schema=".interfaces.ITicket"
       />
  </class>

Now you can add a link in ``collectormain.pt`` like this::

  <a href="@@add_ticket">Add Ticket</a>

When you click on this link, it expects a view. You can create an
AddForm inside ``views.py``::

  from tc.main.interfaces import ITicket

  from tc.main.ticket import Ticket

  class AddTicket(form.AddForm):

      form_fields = form.Fields(ITicket)

      def createAndAdd(self, data):
          number = data['number']
          summary = data['summary']
          ticket = Ticket()
          self.context[number] = ticket
          self.request.response.redirect('.')

You can register the view inside `configure.zcml`::

    <browser:page
       for=".interfaces.ICollector"
       name="add_ticket"
       permission="zope.ManageContent"
       class=".views.AddTicket"
       />

Adding Comments
---------------

.. warning::

   This section is not completed.

In this section, you will create `comment` objects and add it to
tickets.  As the first step, you need to define the interface for the
comments.  You can add this interface definition inside
``interfaces.py``::

  class IComment(Interface):
      """Comment for Ticket"""

      body = Text(
          title=u"Additional Comment",
          description=u"Body of the Comment.",
          default=u"",
          required=True)

Next, you can implement the comment like this::

  from zope.interface import implements

  from tc.main.interfaces import IComment
  from tc.main.interfaces import ICommentContained
  from zope.location.contained import Contained

  class Comment(Contained):

      implements(IComment, ICommentContained)

      body = u""

Then, register the interface & class::

  <interface 
     interface=".interfaces.IComment" 
     type="zope.app.content.interfaces.IContentType"
     /> 

  <class class=".ticket.Comment">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <require
       permission="zope.ManageContent"
       interface=".interfaces.IComment"
       />
    <require
       permission="zope.ManageContent"
       set_schema=".interfaces.IComment"
       />
  </class>

Conclusion
----------

This chapter explored creating content components.  You can learn
more about BlueBream from the :ref:`manual`.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
