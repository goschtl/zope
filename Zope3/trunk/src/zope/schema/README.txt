==============
Zope 3 Schemas
==============


Introduction
------------

Schemas extend the notion of interfaces to descriptions of Attributes
rather than methods.  Every Schema is an interface and specifies the
public fields of an object.  A *Field* roughly corresponds to an
attribute of a python object.  But a Field provides space for a title
and a description.  It can also constrain its value and provide a
validation method.  Besides you can optionally specify characteristics
such as its value beeing readonly or not required.

Zope 3 schemas were born when Jim Fulton and Martijn Faassen thought
about Formulator for Zope 3 and PropertySets while at the `Zope 3
sprint`_ at the `Zope BBQ`_ in Berlin.  They realized that if you strip
all view logic from forms than you have something to interfaces.  And
thus schemas were born.

.. _Zope 3 sprint: http://dev.zope.org/Zope3/ZopeBBQ2002Sprint
.. _Zope BBQ: http://www.beehive.de/zope/Events/ZopeBBQ2002.html


Dependencies
------------

The ``zope.schema`` package only depends on the ``zope.interface``
package.


Simple Usage
------------

::

    $ python
    >>> class Bookmark:
    ...     def __init__(self, url):
    ...         self.url = url
    ...
    >>> from Zope.Schema import TextLine, validateMapping
    >>> from Interface import Interface
    >>> class IBookmark(Interface):
    ...     url = TextLine(title=u'url of the bookmark')
    ...
    ...
    >>> obj = Bookmark(u'zope website', u'http://www.zope.org',
    ...                keywords=('web', 'python'))
    >>> validateMapping(IBookmark, obj.__dict__)

The last statement validates that our object conforms to the
``IBookmark`` Schema.


What is a schema, how does it compare to an interface?
------------------------------------------------------

A schema is an extended interface which defines Fields.  You can
validate that attributes of an object conform to their Fields defined
on the schema.  With plain interfaces you can only validate that
methods conform to their interface specification.

So interfaces and schemas refer to different aspects of an object
(respectively its code and state).

A Schema starts out like an interface but defines certain Fields to
which an object's attributes must conform.  Let's look at a stripped
down example from the programmer's tutorial (chapter two)::

    from Interface import Interface
    from Zope.Schema import Interface, Text, TextLine

    class IContact(Interface):
        """Provides access to basic contact information."""

        first = TextLine(title=u"First name")
        last = TextLine(title=u"Last name")
        email = TextLine(title=u"Electronic mail address")
        address = Text(title=u"Postal address")
        postalCode = TextLine(title=u"Postal code",
                              constraint=re.compile(
                                  "\d{5,5}(-\d{4,4})?$").match)

``TextLine`` is a field and expresses that an attribute is a single line
of unicode text.  ``Text`` expresses an arbitrary unicode ("text")
object.  The most interesting part is the last attribute
specification.  It constrains the ``postalCode`` attribute to only have
values that are US postal codes.

Now we want a class that adheres to the IContact Schema::

    class Contact(Persistence.Persistent):
        __implements__ = IContact

        def __init__(self, first, last, email, address, pc):
            self.first = first
            self.last = last
            self.email = email
            self.address = address
            self.postalCode = pc

Now you can see if an instance of ``Contact`` actually implements the
schema::

    from Zope.App.Schema import validateMapping
    someone = contact('Tim','Roberts', 'tim@roberts', '','')
    validateMapping(IContact, someone.__dict__)


Data Modelling Concepts
-----------------------

XXX much more is needed here!

The ``zope.schema`` package provides a core set of field types,
including single- and multi-line text fields, binary data fields,
integers, floating-point numbers, and date/time values.

Selection issues; field type can specify:

- "Raw" data value

  Simple values not constrained by a selection list.

- Value from enumeration (options provided by schema)

  This models a single selection from a list of possible values
  specified by the schema.  The selection list is expected to be the
  same for all values of the type.  Changes to the list are driven by
  schema evolution.

  This is done by mixing-in the IEnumerated interface into the field
  type, and the Enumerated mixin for the implementation (or emulating
  it in a concrete class).

- Value from selection list (options provided by an object)

  This models a single selection from a list of possible values
  specified by a source outside the schema.  The selection list
  depends entirely on the source of the list, and may vary over time
  and from object to object.  Changes to the list are not related to
  the schema, but changing how the list is determined is based on
  schema evolution.

  There is not currently a spelling of this, but it could be
  facilitated using alternate mixins similar to IEnumerated and
  Enumerated.


Issues to be solved
-------------------

These issues were written up at the `Rotterdam Sprint`_ (12/4/2002).

.. _Rotterdam Sprint: http://dev.zope.org/Zope3/InfraeSprintathon

I18n
****

How i18n interferes with Schemas is not thought out.  In a non-English
context we probably want to have titles and descriptions easily
translatable.  The best idea so far is to use an attribute name
together with its surrounding namespace (Interface-name etc.)  as the
message id used for looking up translations.

Example::

    class book(Interface):
        author = ITextLine()

To get to the And in view, while the widget or widget's messages are
constructed::

    TranslatorService.getMessage('book.author.title', 'DE_DE')

Integration with Interfaces
***************************

How closely are Interfaces and Schema related?  Should they be
refactored into one package?  Currently the Interface package is
outside the Zope namespace and Schema is at Zope.Schema.  Should this
stay this way?  Are Schemas Zope-Specific?

Shouldn't the ``implements()`` function on the interface package be
named ``setImplements()`` as opposed to ``getImplements()``?  This way
if you write::

    setImplements(cls, interface)

it is obvious what you mean (as opposed to ``implements(cls,
interface)`` which could mean *asking* if ``cls`` implements the
interface.

Clarify and clean up use cases
******************************

Some use cases are not easy to understand.  A lot of them look like
features rather than use cases.  The list of schema use cases needs to
be cleaned up and be (sometimes) more detailed.


References
----------

- Use case list, http://dev.zope.org/Zope3/Zope3SchemasUseCases

- Documented interfaces, zope/schema/interfaces.py

- Jim Fulton's Programmers Tutorial; in CVS:
  Docs/ZopeComponentArchitecture/PythonProgrammerTutorial/Chapter2
