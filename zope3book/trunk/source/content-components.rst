Content Components
==================

.. index:: content component; component

Introduction
------------

Of course it is essential for any serious Zope 3 developer to know
how to implement new content objects.  Using the example of a ticket
collector, this chapter will outline the main steps required to
implement and register a new content component in Zope 3.  This
chapter is the beginning of the development of TicketCollector
content type and everything that is to it.

A content component is the component which holds the data of the
application.  See this example::

  >>> from zope.interface import Interface
  >>> from zope.interface import Attribute
  >>> from zope.interface import implements

  >>> class IPerson(Interface):
  ...     name = Attribute("Name")

  >>> class Person(object):
  ...     implements(IPerson)
  ...     name = None

  >>> jack = Person()
  >>> jack.name = "Jack"

Here `jack` is a content component.  So, a content component is
nothing but an object which provides a particular interface.  You can
use ``zope.schema`` to define fields of interface.  This will help to
generate web forms easily.  The above interface can be declared in a
better way like this::

  >>> from zope.schema import TextLine

  >>> class IPerson(Interface):
  ...     name = TextLine(
  ...         title=u"Name",
  ...         description=u"Name of person",
  ...         default=u"",
  ...         required=True)

If you are developing an enterprise application, content components
are the most important thing you have to organize first.  To learn
Zope 3 application development with content components, this chapter
will continue the ticket collector application.


User stories
------------

First look at the user stories, this book will implement these
stories in coming chapters.

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
Zope 3 and add additional functionality.


Interfaces
----------

The very first step of the coding process is always to define your
interfaces, which represent your external API.  You should be aware
that software that is built on top of your packages expect the
interfaces to behave exactly the way you specify them.  This is often
less of an issue for attributes and arguments of a method, but often
enough developers forget to specify what the expected return value of
a method or function is or which exceptions it can raise or catch.

Interfaces are commonly stored in an ``interfaces`` module or
package.  Since our package is not that big, you are going to use a
file-based module; therefore start editing a file called
``interfaces.py`` in your favorite editor.

In this initial step of our application, you are only interested in
defining one interface for the ticket collector itself and one for a
single ticket, which are listed below (add these to the file
``interfaces.py``)::

  from zope.interface import Interface
  from zope.schema import Text, TextLine, Field

  from zope.app.container.constraints import containers, contains
  from zope.app.container.interfaces import IContained, IContainer

  class IComment(Interface):
      """Comment for Ticket"""

      body = Text(
          title=u"Additional Comment",
          description=u"Body of the Comment.",
          default=u"",
          required=True)

  class ITicket(IContainer):
      """A ticket object."""

      summary = TextLine(
          title=u"Summary",
          description=u"Short summary",
          default=u"",
          required=True)
    
      description = Text(
          title=u"Description",
          description=u"Full description",
          default=u"",
          required=False)

      contains('.IComment')

  class ICollector(IContainer):
      """Collector the base object. It can only
      contains ITicket objects."""

      contains('.ITicket')
    
      description = Text(
          title=u"Description",
          description=u"A description of the collector.",
          default=u"",
          required=False)


  class ITicketContained(IContained):
      """Interface that specifies the type of objects that can contain
      tickets.  So a ticket can only contain in a collector."""

      containers(ICollector)

  class ICommentContained(IContained):
      """Interface that specifies the type of objects that can contain
      comments.  So a comment can only contain in a ticket."""

      containers(ITicket)

If you want a hierarchy of comments, the ``IComment`` and
``ICommentContained`` can be changed like this::

  class IComment(Interface):
      """Comment for Ticket"""

      body = Text(
          title=u"Additional Comment",
          description=u"Body of the Comment.",
          default=u"",
          required=True)

      contains('.IComment')

  class ICommentContained(IContained):
      """Interface that specifies the type of objects that can
      contain comments.  So a comment can contain in a ticket or a
      comment itself."""

      containers(ITicket, IComment)

See the ``IComment`` interface calls ``contains`` function with
``.IComment`` as argument.  And in ``ICommentContained`` interface,
``IComment`` is also added.  But for simplicity these interfaces are
not used in this chapter.


Unit tests
----------

Here you can see some boiler-plate code which helps to run the
doctest based unittests which you will write later.  Since
`Collector` and `Ticket` objects are containers, this code also run
common tests for containers.  By convention write all unit test files
under `tests` directory.  But doctest files are placed in the package
directory itself.

First create ``tests/test_collector.py``::

  import unittest
  from zope.testing.doctestunit import DocTestSuite

  from zope.app.container.tests.test_icontainer import TestSampleContainer

  from collector.ticketcollector import Collector


  class Test(TestSampleContainer):

      def makeTestObject(self):
          return Collector()

  def test_suite():
      return unittest.TestSuite((
          DocTestSuite('collector.ticketcollector'),
          unittest.makeSuite(Test),
          ))

  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')


Then ``tests/test_ticket.py``::

  import unittest
  from zope.testing.doctestunit import DocTestSuite

  from zope.app.container.tests.test_icontainer import TestSampleContainer

  from collector.ticket import Ticket


  class Test(TestSampleContainer):

      def makeTestObject(self):
          return Ticket()

  def test_suite():
      return unittest.TestSuite((
          DocTestSuite('collector.ticket'),
          unittest.makeSuite(Test),
          ))

  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')

``tests/test_comment.py``::

  import unittest
  from zope.testing.doctestunit import DocTestSuite

  def test_suite():
      return unittest.TestSuite((
          DocTestSuite('collector.comment'),
          ))

  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')

To run the unit test::

  $ ./bin/buildout
  $ ./bin/test

Of course now all tests should fail.  In next section you will write
doctests along with implemetation.


Implementation
--------------

As you can see in the unit test module, collector is going to be
implemented in ``ticketcollector.py``.  A base class,
``BTreeContainer`` is used to implement the container.  This will
make the implementation easier.

Here is the ``ticketcollector.py``::

  from zope.interface import implements
  from zope.app.container.btree import BTreeContainer

  from interfaces import ICollector

  class Collector(BTreeContainer):
      """A simple implementation of a collector using B-Tree Containers.

      Make sure that the ``Collector`` implements the ``ICollector``
      interface::

        >>> from zope.interface.verify import verifyClass
        >>> verifyClass(ICollector, Collector)
        True
    
      Here is an example of changing the description of the collector::

        >>> collector = Collector()
        >>> collector.description
        u''
        >>> collector.description = u'Ticket Collector Description'
        >>> collector.description
        u'Ticket Collector Description'
      """

      implements(ICollector)

      description = u''


Similarly ``ticket.py``::

  from zope.interface import implements
  from zope.interface import classProvides
  from zope.app.container.btree import BTreeContainer
  from zope.app.container.contained import Contained

  from interfaces import ITicket, ITicketContained

  class Ticket(BTreeContainer, Contained):
      """A simple implementation of a ticket using B-Tree Containers.

      Make sure that the ``Ticket`` implements the ``ITicket`` interface::

        >>> from zope.interface.verify import verifyClass
        >>> verifyClass(ITicket, Ticket)
        True

      Here is an example of changing the summary and description of the ticket::

        >>> ticket = Ticket()
        >>> ticket.summary
        u''
        >>> ticket.description
        u''
        >>> ticket.summary = u'Ticket Summary'
        >>> ticket.description = u'Ticket Description'
        >>> ticket.summary
        u'Ticket Summary'
        >>> ticket.description
        u'Ticket Description'
      """

      implements(ITicket, ITicketContained)

      summary = u''
      description = u''

Then `comment.py`::

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


Registration
------------

You have written interfaces and its implementations, now how to bind
this with Zope 3 framework.  You can use use Zope Configuration
Markup Language (ZCML) based configuration file for this.

This is our ``configure.zcml``::

  <configure
      xmlns="http://namespaces.zope.org/zope"
      i18n_domain="collector">

    <interface 
        interface=".interfaces.ICollector" 
        type="zope.app.content.interfaces.IContentType"
        /> 

    <class class=".ticketcollector.Collector">
      <implements
          interface="zope.annotation.interfaces.IAttributeAnnotatable"
          />
      <implements
          interface="zope.app.container.interfaces.IContentContainer" 
          />
      <require
          permission="zope.ManageContent"
          set_schema=".interfaces.ICollector"
          />
      <require
          permission="zope.ManageContent"
          interface=".interfaces.ICollector"
          />
    </class>

    <interface 
        interface=".interfaces.ITicket" 
        type="zope.app.content.interfaces.IContentType"
        /> 

    <class class=".ticket.Ticket">
      <implements
          interface="zope.annotation.interfaces.IAttributeAnnotatable"
          />
      <implements
          interface="zope.app.container.interfaces.IContentContainer" 
          />
      <require
          permission="zope.ManageContent"
          set_schema=".interfaces.ITicket"
          />
      <require
          permission="zope.ManageContent"
          interface=".interfaces.ITicket"
          />
    </class>

    <interface 
        interface=".interfaces.IComment" 
        type="zope.app.content.interfaces.IContentType"
        /> 

    <class class=".comment.Comment">
      <implements
          interface="zope.annotation.interfaces.IAttributeAnnotatable"
          />
      <require
          permission="zope.ManageContent"
          set_schema=".interfaces.IComment"
          />
      <require
          permission="zope.ManageContent"
          interface=".interfaces.IComment"
          />
    </class>

    <include package=".browser" />

  </configure>


Running application
-------------------

Before running the applcation create one view for ``Collector``.

Create a `browser` directory and under that, a new `configure.zcml`
file::

  <configure
      xmlns="http://namespaces.zope.org/browser">

    <addMenuItem
        class="ticketcollector.ticketcollector.Collector"
        title="Collector"
        description="A Collector"
        permission="zope.ManageContent"
        />

  </configure>

The ``class`` attribute specifies the module path for the class, a
leading dot means to make the import relative to the package
containing the ZCML file.  Therefore in this case Zope will import
the ticketcollector.ticketcollector module, then import "Collector" from
that module.

The ``title`` attribute provides the title to display in the add
menu.

The ``permission`` attribute is used to describe what permission is
required for a person to be able to add one of these objects.  The
``zope.ManageContent`` permission means that the user can add,
remove, and modify content (the "admin" user you created while making
the instance is one such user).

You have to tell Zope to read our ZCML file, and the easiest way to
do that is to put a "slug" in the ``applcation.zcml``.  A ``slug`` is
a ZCML file that just includes another file.  Here's what our slug
should look like::

  <include package="ticketcollector" />

Now if you start Zope back up, you can go to the ZMI and add our
content type by clicking on "Add Collector" and entering a name for
our object; name it "MyCollector".

Views
-----


Functional testing
------------------


Summary
-------

This chapter introduced content components.
