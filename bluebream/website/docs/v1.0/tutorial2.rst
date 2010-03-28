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
be noticed that, every content component, including container
components has well defined interfaces.

This chapter explore content components in more detail.  After
completing this chapter, you should be able to:

- Define schema for content components
- Create container objects
- Use ZCML to configure various components

Before proceeding further, here is an overview of sections:

- **Adding tickets** -- This section shows creating a ticket
  collector objects.  This section provide a detailed overview of
  creating content object and demonstrate with a simple example.

- **Listing tickets** -- This section shows displaying tickets from
  the main collector page.

- **Adding comments** -- This section explain about adding content
  object inside other container objects.  Ticket objects will be
  transformed to a container object.

- **Listing comments** -- This section shows displaying tickets from
  the ticket page.

.. note::

   The examples in this documentation can be downloaded from here:
   http://download.zope.org/bluebream/examples/ticketcollector-1.0.0.tar.bz2

.. _tut2-adding-tickets:

Adding tickets
--------------

Schema definition
~~~~~~~~~~~~~~~~~

In this section, you will learn about adding tickets to collector.
In order to use ticket objects, first you need to create an interface
for tickets.  Update the ``src/tc/collector/interfaces.py`` with the ticket
interface::

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


The ``TextLine`` and ``Text`` are already imported, if not, you can
import it from these locations::

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
ticket objects are allowed inside collector.  You need to move the
definition of ``ITicket`` above the ``IContainer`` as the ``ITicket``
being used there.  Add the following method definition to
``ICollector`` class::

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

Next, you can implement this interface inside ``src/tc/collector/ticket.py``::

  from zope.interface import implements
  from tc.collector.interfaces import ITicket
  from tc.collector.interfaces import ITicketContained
  from zope.container.contained import Contained


  class Ticket(BTreeContainer, Contained):

      implements(ITicket, ITicketContained)

      number = u""
      summary = u""

Configuration
~~~~~~~~~~~~~

Then, register the interface & class.  Open the
``src/tc/collector/configure.zcml`` and update it with these details::

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
       permission="zope.ManageContent"
       interface="tc.collector.interfaces.ITicket"
       />
    <require
       permission="zope.ManageContent"
       set_schema="tc.collector.interfaces.ITicket"
       />
  </class>

Now you can add a link to ``@@add_ticket`` in
``src/tc/collector/collectormain.pt``.  Now the template will look like
this::

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
AddForm inside ``src/tc/collector/views.py``::

  from tc.collector.interfaces import ITicket

  from tc.collector.ticket import Ticket

  class AddTicket(form.AddForm):

      form_fields = form.Fields(ITicket)

      def createAndAdd(self, data):
          number = data['number']
          summary = data['summary']
          ticket = Ticket()
          self.context[number] = ticket
          self.request.response.redirect('.')

You can register the view inside ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="add_ticket"
     permission="zope.ManageContent"
     class="tc.collector.views.AddTicket"
     />

You can add a ticket by visiting:
http://localhost:8080/mycollector/@@add_ticket You can give the ticket
number as '1' and provide summary as 'Test Summary'.

You can check the object from debug shell::

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

Now there is no default browser page for tickets.  If you try to
access the ticket from the URL: http://localhost:8080/mycollector/1 ,
you will get ``NotFound`` error like this::

  URL: http://localhost:8080/mycollector/1
  ...
  NotFound: Object: <tc.collector.ticketcollector.Ticket object at 0x8fe74ac>, name: u'@@index'

This error is raised, because there is no view named ``index``
registered for ``ITicket``.  This section will show how to create a
default view for ``ITicket`` interface.

As you have already seen in the :ref:`started-getting` chapter, you
can create a simple view and register it from ZCML.

In the ``src/tc/collector/views.py`` add a new view like this::

  class TicketMainView(form.DisplayForm):

      form_fields = form.Fields(ITicket)

      template = ViewPageTemplateFile("ticketmain.pt")

You can create the template file here:
``src/tc/collector/ticketmain.pt`` with this content::

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

Then, in the ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="index"
     permission="zope.Public"
     class="tc.collector.views.TicketMainView"
     />

Now you can visit: http://localhost:8080/mycollector/1/@@index It
should display the ticket number and summary.  If you open the HTML
source from browser, it will look like this::

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

Listing tickets
---------------

This section explain listing tickets in the main collector page, so
that the user can navigate to ticket and see the details.

To list the tikets in the main collector page, you need to modify the
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
``src/main/tc/collector/views.py`` file::

    class TicketCollectorMainView(form.DisplayForm):

        form_fields = form.Fields(ICollector)

        template = ViewPageTemplateFile("collectormain.pt")

        def getTickets(self):
            tickets = []
            for ticket in self.context.values():
                tickets.append({'url': ticket.number+"/@@index",
                                'summary': ticket.summary})
            return tickets

Adding Comments
---------------

.. warning:: This section is incomplete

In this section, you will create `comment` objects and add it to
tickets.  As the first step, you need to define the interface for the
comments.  You can add this interface definition inside
``src/tc/collector/interfaces.py``::

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

Next, you can implement the comment like this.  You can create a new
file for the implementation, ``src/tc/collector/comment.py``::

  from zope.interface import implements
  from tc.collector.interfaces import IComment
  from tc.collector.interfaces import ICommentContained
  from zope.container.contained import Contained

  class Comment(Contained):

      implements(IComment, ICommentContained)

      body = u""

Then, register the interface & class::

  <interface
     interface="tc.collector.interfaces.IComment"
     type="zope.app.content.interfaces.IContentType"
     />

  <class class="tc.collector.comment.Comment">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <require
       permission="zope.ManageContent"
       interface="tc.collector.interfaces.IComment"
       />
    <require
       permission="zope.ManageContent"
       set_schema="tc.collector.interfaces.IComment"
       />
  </class>

You can add ``ItemTypePrecondition`` to ``ITicket``.  Open the
``src/tc/collector/interfaces.py`` and update the interface definition::

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

Update the ticket implementation at ``src/tc/collector/ticket.py``::

  from zope.interface import implements
  from tc.collector.interfaces import ITicket
  from tc.collector.interfaces import ITicketContained
  from zope.container.contained import Contained
  from zope.container.btree import BTreeContainer


  class Ticket(BTreeContainer, Contained):

      implements(ITicket, ITicketContained)

      number = u""
      summary = u""

You can update the template file here:
``src/tc/collector/ticketmain.pt`` with this content::

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
``src/tc/collector/views.py`` file and update with the ``AddComment`` form
given below::

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

You can register the view inside ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ITicket"
     name="add_comment"
     permission="zope.ManageContent"
     class="tc.collector.views.AddComment"
     />

Listing comments
----------------

This section explain listing tickets in the ticket page, so that the
user can see comments for the particular ticket.

To list the comments in the ticket page, you need to modify the
``src/tc/collector/ticketmain.pt``::

  <html>
  <head>
  <title>Welcome to ticket collector!</title>
  </head>
  <body>

  Welcome to ticket collector! <br/> <br/>

  <a href="@@add_ticket">Add Ticket</a> <br/> <br/>

  <p tal:repeat="ticket context/values">
    <span tal:content="ticket/body">Comment goes here</span>
  </p>

  </body>
  </html>

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
