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
to:

- Create content components
- Change the look and feel
- Use catalog to search

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


.. _tut2-adding-tickets:

Change the look and feel
------------------------

Searching tickets
-----------------

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
