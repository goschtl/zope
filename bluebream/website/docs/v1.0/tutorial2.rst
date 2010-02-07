.. _tut2-tutorial:

Tutorial --- Part 2
===================

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

Introduction
------------

This is the second part of tutorial.  This chapter expand the
application started in the first part of tutorial with additional
functionalities.  If you complete this chapter, you should be able
to:

- Create content components
- Change the look and feel
- Using catalog to search

Adding tickets and comments
---------------------------

In this section, you will learn about adding tickets and comments to
collector.

::

  class ITicket(Interface):
     """Ticket - the main content object"""

      name = TextLine(
          title=u"Name",
          description=u"Name of application.",
          default=u"",
          required=True)

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
