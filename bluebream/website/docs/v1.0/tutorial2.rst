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

This is the second part of tutorial.  This chapter expand the
application started in the first part of tutorial with additional
functionalities.  If you complete this chapter, you should be able
to create content components.

.. _tut2-adding-tickets:

Adding tickets
--------------

In this section, you will learn about adding tickets to collector.
In order to use ticket objects, first you need to create an interface
for tickets.  Update the ``interfaces.py`` with the ticket
interface::

  class ITicket(Interface):
     """Ticket - the main content object"""

      name = TextLine(
          title=u"Name",
          description=u"Name of application.",
          default=u"",
          required=True)

      summary = TextLine(
          title=u"Summary",
          description=u"Ticket summary",
          default=u"",
          required=True)

Next, you can implement this interface inside ``ticket.py``::

  from zope.interface import implements
  from tc.main.interfaces import ITicket
  from tc.main.interfaces import ITicketContained
  from zope.location.contained import Contained


  class Ticket(Contained):

      implements(ITicket, ITicketContained)

      number = u""
      summary = u""

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
