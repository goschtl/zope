.. _tut2-tutorial:

Tutorial --- Part 2
===================

.. _tut2-intro:

Introduction
------------

This is the second part of the tutorial.  In the first part, you learned
about project directory structure, Buildout configuration, content
components and using the form library.  Content components are
objects with a user visible view.  A view could be a browser view
(HTML/JS/CSS) or JSON or XMLRPC or any other view.  To explain the
idea of content components, the ticket collector project started in
the first part of tutorial will be expanded with additional
functionality.  In fact, the collector object created in the last
chapter is a content component.  In this chapter, you will create new
content objects like tickets and comments.  Another thing that should
be noted is that every content component, including container
components, has well defined interfaces.

This chapter explores content components in more detail.  After
completing this chapter, you should be able to:

- Define schema for content components
- Create container objects
- Use ZCML to configure various components

Before proceeding further, here is an overview of what we will cover:

- **Adding tickets** -- In this section you will create a ticket
  object. We provide a detailed overview of creating content objects
  and demonstrate with a simple example.

- **Listing tickets** -- Next you will see how to display tickets
  from the main collector page.

- **Adding comments** -- Here you will learn how to add content
  objects inside other container objects. Ticket objects will be
  transformed to container objects.

- **Listing comments** -- In this section you will develop a comment
  object and write the code needed to display comments on the ticket page.

.. note::

   The examples in this documentation can be downloaded from here:
   http://download.zope.org/bluebream/examples/ticketcollector-1.0.0.tar.bz2

   The source code is available in different stages corresponding to
   sections.

   - Stage 1 : Section 5.2 to 5.7
   - Stage 2 : Section 5.8
   - Stage 3 : Section 5.9
   - Stage 4 : Section 6.2
   - Stage 5 : Section 6.3
   - Stage 6 : Section 6.4 & 6.5

.. _tut2-adding-tickets:

Adding tickets
--------------

Schema definition
~~~~~~~~~~~~~~~~~

In this section, you will learn how to add tickets to a collector.
In order to use ticket objects, first you need to create an interface
for tickets.  Update ``src/tc/collector/interfaces.py`` with the ticket
interface::

  from zope.container.interfaces import IContainer

  class ITicket(IContainer):
      """Ticket - the ticket content component"""

      number = TextLine(
          title=u"Number",
          description=u"Ticket number",
          default=u"",
          required=True)

      summary = Text(
          title=u"Summary",
          description=u"Ticket summary",
          default=u"",
          required=True)


The ``TextLine`` and ``Text`` should already have been imported, if
not, you can import them::

  from zope.schema import TextLine
  from zope.schema import Text

It would be good if you set a precondition to restrict what types of
objects you want to add inside a collector.  If you know that you
only expect ticket objects inside a collector object, you can add a
precondition to ensure that no other types of object can be added to
a collector.  To do this, you need to add a ``__setitem__`` method to
``ICollector`` the interface definition (The ``__setitem__`` is part
of ``IContainer`` API).  Then below that, you can add the
``precondition`` attribute, which is an instance of the
``ItemTypePrecondition`` class.  You can pass the interfaces as
arguments to the ``ItemTypePrecondition`` class.  Below, only one
class (``ITicket``) is passed.  So, only ticket objects are allowed
inside a collector.  You need to move the definition of ``ITicket``
above the ``IContainer`` as the ``ITicket`` is used by it.  Add the
following method definition to the ``ICollector`` class::

    from zope.container.constraints import ItemTypePrecondition

    def __setitem__(name, object):
        """Add an ICollector object."""

    __setitem__.precondition = ItemTypePrecondition(ITicket)

The ``ItemTypePrecondition`` provides a way to restrict the type of
object which can be added inside a container.  You can also specify
that ticket objects can be only added inside a collector.  To do
this, you need to create another interface inheriting from
``zope.container.interfaces.IContained``.

::

  from zope.schema import Field
  from zope.container.interfaces import IContained
  from zope.container.constraints import ContainerTypesConstraint

  class ITicketContained(IContained):
      """Interface that specifies the type of objects that can contain
      tickets.  So a ticket can only contain in a collector."""

      __parent__ = Field(
          constraint = ContainerTypesConstraint(ICollector))

Here you added a constraint for ``__parent__`` field using the
``ContainerTypesConstraint`` class.

Implementation
~~~~~~~~~~~~~~

Next, you can implement this interface inside
``src/tc/collector/ticket.py``::

  from zope.interface import implements
  from zope.container.contained import Contained
  from zope.container.btree import BTreeContainer

  from tc.collector.interfaces import ITicket
  from tc.collector.interfaces import ITicketContained


  class Ticket(BTreeContainer, Contained):

      implements(ITicket, ITicketContained)

      number = u""
      summary = u""

Configuration
~~~~~~~~~~~~~

Then, register the interface & class.  Open
``src/tc/collector/configure.zcml`` and update it with these
details::

  <interface
     interface="tc.collector.interfaces.ITicket"
     type="zope.app.content.interfaces.IContentType"
     />

  <class class="tc.collector.ticket.Ticket">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <implements
       interface="zope.container.interfaces.IContentContainer" 
       />
    <require
       permission="zope.Public"
       interface="tc.collector.interfaces.ITicket"
       />
    <require
       permission="zope.Public"
       set_schema="tc.collector.interfaces.ITicket"
       />
  </class>

Now you can add a link to ``@@add_ticket`` in
``src/tc/collector/collectormain.pt``.  Now the template will look
like this::

  <html>
  <head>
  <title>Welcome to ticket collector</title>
  </head>
  <body>

  Welcome to ticket collector! <br/> <br/>

  <a href="@@add_ticket">Add Ticket</a>

  </body>
  </html>

When you click on this link, it expects a view. You can create an
AddForm in ``src/tc/collector/views.py``::

  from tc.collector.interfaces import ITicket

  from tc.collector.ticket import Ticket

  class AddTicket(form.AddForm):

      form_fields = form.Fields(ITicket)

      def createAndAdd(self, data):
          number = data['number']
          summary = data['summary']
          ticket = Ticket()
          ticket.number = number
          ticket.summary = summary
          self.context[number] = ticket
          self.request.response.redirect('.')

You can register the view in ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="add_ticket"
     permission="zope.Public"
     class="tc.collector.views.AddTicket"
     />

You can add a ticket by visiting:
http://localhost:8080/mycollector/@@add_ticket You can give the
ticket number as '1' and provide 'Test Summary' as the summary.

You can then check the object from the debug shell::

  jack@computer:/projects/ticketcollector$ ./bin/paster shell debug.ini
  ...
  Welcome to the interactive debug prompt.
  The 'root' variable contains the ZODB root folder.
  The 'app' variable contains the Debugger, 'app.publish(path)' simulates a request.
  >>> root['mycollector']
  <tc.collector.ticketcollector.Collector object at 0xa5fc96c>
  >>> root['mycollector']['1']
  <tc.collector.ticket.Ticket object at 0xa5ffecc>

Default browser page for tickets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We do not yet have a default browser page for tickets.  If you try to
access the ticket from the URL: http://localhost:8080/mycollector/1 ,
you will get ``NotFound`` error like this::

  URL: http://localhost:8080/mycollector/1
  ...
  NotFound: Object: <tc.collector.ticketcollector.Ticket object at 0x8fe74ac>, name: u'@@index'

This error is raised because there is no view named ``index``
registered for ``ITicket``.  This section will show how to create a
default view for ``ITicket`` interface.

As you have already seen in the :ref:`started-getting` chapter, you
can create a simple view and register it from ZCML.

In ``src/tc/collector/views.py`` add a new view like this::

  class TicketMainView(form.DisplayForm):

      form_fields = form.Fields(ITicket)

      template = ViewPageTemplateFile("ticketmain.pt")

You can create the template file ``src/tc/collector/ticketmain.pt``
with this content::

  <html>
  <head>
  <title>Welcome to ticket collector!</title>
  </head>
  <body>

  You are looking at ticket number:
  <b tal:content="context/number">number</b>

  <h3>Summary</h3>

  <p tal:content="context/summary">Summary goes here</p>

  </body>
  </html>

Then, in ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="index"
     permission="zope.Public"
     class="tc.collector.views.TicketMainView"
     />

Now you can visit: http://localhost:8080/mycollector/1/@@index It
should display the ticket number and summary.  If you view the HTML
source with your browser, it will look like this::

  <html>
  <head>
  <title>Welcome to ticket collector!</title>
  </head>
  <body>

  You are looking at ticket number: <b>1</b>

  <h3>Summary</h3>

  <p>Test Summary</p>

  </body>
  </html>

.. _tut2-listing-tickets:

Listing tickets
---------------

This section explains how to list tickets on the main collector page,
so that the user can navigate to a ticket and see its details.

To list the tickets on the main collector page, you need to modify
``src/tc/collector/collectormain.pt``::

  <html>
  <head>
  <title>Welcome to ticket collector!</title>
  </head>
  <body>

  Welcome to ticket collector! <br/> <br/>

  <a href="@@add_ticket">Add Ticket</a> <br/> <br/>

  <ol>
    <li tal:repeat="ticket view/getTickets">
      <a href=""
         tal:attributes="href ticket/url"
         tal:content="ticket/summary">Ticket Summary</a>
    </li>
  </ol>

  </body>
  </html>

You need to change the ``TicketCollectorMainView`` defined in
``src/tc/collector/views.py``::

    class TicketCollectorMainView(form.DisplayForm):

        form_fields = form.Fields(ICollector)

        template = ViewPageTemplateFile("collectormain.pt")

        def getTickets(self):
            tickets = []
            for ticket in self.context.values():
                tickets.append({'url': ticket.number+"/@@index",
                                'summary': ticket.summary})
            return tickets

.. _tut2-adding-comments:

Adding Comments
---------------

.. warning:: This section is incomplete

In this section, you will create `comment` objects which can be added
to tickets.  As the first step, you need to define the interface for
a comment.  You can add this interface definition in
``src/tc/collector/interfaces.py``::

  from zope.interface import Interface

  class IComment(Interface):
      """Comment for Ticket"""

      body = Text(
          title=u"Additional Comment",
          description=u"Body of the Comment.",
          default=u"",
          required=True)

  class ICommentContained(IContained):
      """Interface that specifies the type of objects that can contain
      comments.  A comment can only contain in a ticket."""

      __parent__ = Field(
          constraint = ContainerTypesConstraint(ITicket))

To implement the comment, you can create a new file for the
implementation, ``src/tc/collector/comment.py``::

  from zope.interface import implements
  from tc.collector.interfaces import IComment
  from tc.collector.interfaces import ICommentContained
  from zope.container.contained import Contained

  class Comment(Contained):

      implements(IComment, ICommentContained)

      body = u""

Then, register the interface & class, Upate the
``src/tc/collector/configure.zcml`` file::

  <interface
     interface="tc.collector.interfaces.IComment"
     type="zope.app.content.interfaces.IContentType"
     />

  <class class="tc.collector.comment.Comment">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <require
       permission="zope.Public"
       interface="tc.collector.interfaces.IComment"
       />
    <require
       permission="zope.Public"
       set_schema="tc.collector.interfaces.IComment"
       />
  </class>

You can add ``ItemTypePrecondition`` to ``ITicket``.  Open
``src/tc/collector/interfaces.py`` and update the interface
definition::

  class ITicket(IContainer):
      """Ticket - the ticket content component"""

      number = TextLine(
          title=u"Number",
          description=u"Ticket number",
          default=u"",
          required=True)

      summary = Text(
          title=u"Summary",
          description=u"Ticket summary",
          default=u"",
          required=True)

      def __setitem__(name, object):
          """Add an ICollector object."""

      __setitem__.precondition = ItemTypePrecondition(IComment)

You can update the template file ``src/tc/collector/ticketmain.pt``
with this content::

  <html>
  <head>
  <title>Welcome to ticket collector!</title>
  </head>
  <body>

  You are looking at ticket number:
  <b tal:content="context/number">number</b>

  <h3>Summary</h3>

  <p tal:content="context/summary">Summary goes here</p>

  <a href="@@add_comment">Add Comment</a>

  </body>
  </html>

You need to create an ``AddForm`` like this.  Open the
``src/tc/collector/views.py`` file and update with the ``AddComment``
form given below::

  from zope.container.interfaces import INameChooser
  from tc.collector.interfaces import IComment
  from tc.collector.comment import Comment

  class AddComment(form.AddForm):

      form_fields = form.Fields(IComment)

      def createAndAdd(self, data):
          body = data['body']
          comment = Comment()
          comment.body = body
          namechooser = INameChooser(self.context)
          number = namechooser.chooseName('c', comment)
          self.context[number] = comment
          self.request.response.redirect('.')

You can register the view in ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="add_comment"
     permission="zope.Public"
     class="tc.collector.views.AddComment"
     />

.. _tut2-listing-comments:

Listing comments
----------------

This section covers listing comments on the ticket page, so that the
user can see comments for the particular ticket.

To list the comments on the ticket page, you need to modify
``src/tc/collector/ticketmain.pt``::


  <html>
  <head>
  <title>Welcome to ticket collector!</title>
  </head>
  <body>

  You are looking at ticket number:
  <b tal:content="context/number">number</b>

  <h3>Summary</h3>

  <p tal:content="context/summary">Summary goes here</p>

  <a href="@@add_comment">Add Comment</a>

  <p tal:repeat="ticket context/values">
    <span tal:content="ticket/body">Comment goes here</span>
  </p>

  </body>
  </html>

.. _tut2-conclusion:

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
