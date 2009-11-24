.. -*- coding: utf-8 -*-
Schema To JSON
**************

Introduction
============

``z3c.schema2json`` can take objects enriched with schema definitions
into the popular JSON serialisation format. It is also capable of 
converting this JSON back into objects. 

This package requires ``simplejson`` or Python version 2.6 (which has
simplejson as part of the standard library). 

Only object attributes described by zope schema are recognised by 
this package. Any attributes that do no have corresponding schema 
descriptions will be lost in the serialization/deserialization process.

Serialization
=============

Let's first define a simple Zope 3 schema::

    >>> from zope import interface, schema
    >>> class IName(interface.Interface):
    ...     first_name = schema.TextLine(title=u'First name')
    ...     last_name = schema.TextLine(title=u'Last name')

Let's now create a class that implements this schema::

    >>> from zope.interface import implements
    >>> class Name(object):
    ...     implements(IName)
    ...     def __init__(self, first_name, last_name):
    ...         self.first_name = first_name
    ...         self.last_name = last_name

Now we make an instance of the class::

    >>> name = Name('Paul', 'Tom')

Now let's serialize it to JSON::
    
    >>> from z3c.schema2json import serialize
    >>> print serialize(IName, name)
    {
      "first_name": "Paul",
      "last_name": "Tom"
    }

We can also serialise other fields too::

    >>> from zope import interface, schema
    >>> class IAddress(interface.Interface):
    ...     street_name = schema.TextLine(title=u'Street name')
    ...     number = schema.Int(title=u'House Number')
    >>> class Address(object):
    ...     implements(IAddress)
    ...     def __init__(self, street_name, number):
    ...         self.street_name = street_name
    ...         self.number = number
    >>> address = Address('Pendle Road', 15)
    >>> print serialize(IAddress, address)
    {
      "number": 15,
      "street_name": "Pendle Road"
    }

A schema can define an ``Object`` field with its own schema, which the
serialisation process can handle::

    >>> class IPerson(interface.Interface):
    ...     name = schema.Object(title=u"Name", schema=IName)
    ...     address =schema.Object(title=u"Address", schema=IAddress)

    >>> class Person(object):
    ...     implements(IPerson)
    ...     def __init__(self, name, address):
    ...         self.name = name
    ...         self.address = address

    >>> person = Person(name, address)
    >>> print serialize(IPerson, person)
    {
      "address": {
        "number": 15,
        "street_name": "Pendle Road"
      },
      "name": {
        "first_name": "Paul",
        "last_name": "Tom"
      }
    }

The serialisation process also works for the List schema type containing
elements with their own schema::

    >>> class ICommission(interface.Interface):
    ...     members = schema.List(
    ...         title = u"Commission",
    ...         value_type=schema.Object(__name__='person',
    ...         schema=IPerson))

Note that we have to explicitly specify __name__ for the field that's
used for value_type here, otherwise we have no name to serialize to
JSON with::

    >>> class Commission(object):
    ...     implements(ICommission)
    ...     def __init__(self, members):
    ...         self.members = members

    >>> commission = Commission(
    ...     [person, Person(Name('Jim', 'Bo'), Address('Sci Road', 3))])
    >>> print serialize(ICommission, commission)
    {
      "members": [
        {
          "address": {
            "number": 15,
            "street_name": "Pendle Road"
          },
          "name": {
            "first_name": "Paul",
            "last_name": "Tom"
          }
        },
        {
          "address": {
            "number": 3,
            "street_name": "Sci Road"
          },
          "name": {
            "first_name": "Jim",
            "last_name": "Bo"
          }
        }
      ]
    }

We get an adapter lookup failure whenever we attempt to serialize a field
type which there's no serializer::

    >>> class IWithNonSerializableField(interface.Interface):
    ...    field = schema.Field(title=u"Commission")
    >>> class NotSerializable(object):
    ...     implements(IWithNonSerializableField)
    ...     def __init__(self, value):  
    ...         self.field = value
    >>> not_serializable = NotSerializable(None)
    >>> serialize(IWithNonSerializableField, not_serializable)
    Traceback (most recent call last):
     ...
    TypeError: ('Could not adapt', <zope.schema._bootstrapfields.Field object at ...>, <InterfaceClass z3c.schema2json._schema2json.IJSONGenerator>)

List fields an also contain more primitive values (rather than Objects) such as Ints::

    >>> class ILottery(interface.Interface):
    ...     numbers = schema.List(
    ...         title = u"Lottery Numbers",
    ...         value_type = schema.Int(title=u"A Lottery Number",
    ...                                 min=0, max=49))
    >>> class Lottery(object):
    ...     implements(ILottery)
    ...     def __init__(self, numbers):
    ...         self.numbers = numbers
    ...
    >>> lotto = Lottery([10, 17, 20, 21, 23, 31, 32])
    >>> print serialize(ILottery, lotto)
    {
       "numbers": [
        10,
        17,
        20,
        21,
        23,
        31,
        32
      ]
    }


Deserialization
===============

Now we would like to take some objects represented as JSON strings and 
deserialize them::

    >>> from z3c.schema2json import deserialize
    >>> json = '''
    ... {
    ...   "first_name": "Guido",
    ...   "last_name": "Van Rossum"
    ... }
    ... '''
    ... name = Name('', '')
    >>> deserialize(json, IName, name)
    >>> name.first_name
    u'Guido'
    >>> name.last_name
    u'Van Rossum'

The order of the fields in the JSON string is irrelevant::

    >>> json = '''
    ... {
    ...   "last_name": "Van Rossum",
    ...   "first_name": "Guido"
    ... }
    ... '''
    ... name = Name('', '')
    >>> deserialize(json, IName, name)
    >>> name.first_name
    u'Guido'
    >>> name.last_name
    u'Van Rossum'

After deserialization, the object ``alsoProvides`` the schema interface::

    >>> IName.providedBy(name)
    True

This also works for other kinds of fields::

    >>> json = '''
    ... {
    ...   "street_name": "Baker Street",
    ...   "number": 221
    ... }
    ... '''
    >>> address = Address('',0)
    >>> deserialize(json, IAddress, address)
    >>> address.street_name
    u'Baker Street'
    >>> address.number
    221

If a schema defines an Object field with its own schema, the serialization
can also handle this::

    >>> json = '''
    ... {
    ...   "name": {
    ...      "first_name": "Sherlock",
    ...      "last_name": "Holmes"
    ...    },
    ...   "address": {
    ...      "street_name": "Baker Street",
    ...      "number": 221
    ...    }
    ... }
    ... '''
    >>> person = Person(Name('', ''), Address('', 0))
    >>> deserialize(json, IPerson, person)
    >>> person.name.first_name
    u'Sherlock'
    >>> person.name.last_name
    u'Holmes'
    >>> person.address.street_name
    u'Baker Street'
    >>> person.address.number
    221
    >>> IPerson.providedBy(person)
    True
    >>> IName.providedBy(person.name)
    True
    >>> IAddress.providedBy(person.address)
    True

Again the order in which the fields come in JSON shouldn't matter::

    >>> json = '''
    ... {
    ...   "address": {
    ...     "number": 221,
    ...     "street_name": "Baker Street"
    ...   },
    ...   "name": {
    ...     "last_name": "Holmes",
    ...     "first_name": "Sherlock"
    ...    }
    ... }
    ... '''   
    >>> person = Person(Name('', ''), Address('', 0))
    >>> deserialize(json, IPerson, person)
    >>> person.name.first_name
    u'Sherlock'
    >>> person.name.last_name
    u'Holmes'
    >>> person.address.street_name
    u'Baker Street'
    >>> person.address.number
    221
    >>> IPerson.providedBy(person)
    True
    >>> IName.providedBy(person.name)
    True
    >>> IAddress.providedBy(person.address)
    True

We can deserialise List types also::

    >>> json = '''
    ... {
    ...   "members": [
    ...    {
    ...       "name": {
    ...         "first_name": "Melanie",
    ...         "last_name": "Parker"
    ...       },
    ...       "address": {
    ...         "street_name": "Chaigley Court",
    ...         "number": 23
    ...      }
    ...     },
    ...     {
    ...       "name": {
    ...         "first_name": "Rob",
    ...         "last_name": "Hall"
    ...       },
    ...       "address": {
    ...         "street_name": "Queenswood Mount",
    ...         "number": 2
    ...       }
    ...     }
    ...   ]
    ... }
    ... '''

    >>> commission = Commission([])
    >>> deserialize(json, ICommission, commission)
    >>> len(commission.members)
    2
    >>> member = commission.members[0]
    >>> member.name.first_name
    u'Melanie'
    >>> member.address.street_name
    u'Chaigley Court'
    >>> member = commission.members[1]
    >>> member.name.first_name
    u'Rob'
    >>> member.address.street_name
    u'Queenswood Mount'

Whenever an item is null, the resulting value should be None::

    >>> json = '''
    ... {
    ...   "first_name": "",
    ...   "last_name": null
    ... }
    ... '''
    >>> name = Name('', '')
    >>> deserialize(json, IName, name)
    >>> name.first_name == ''
    True
    >>> name.last_name is None
    True

For all kinds of fields, like strings and ints...::

    >>> json = '''
    ... {
    ...    "street_name": null,
    ...    "number": null
    ... }
    ... '''
    >>> address = Address('', 0)
    >>> deserialize(json, IAddress, address)
    >>> address.street_name is None
    True
    >>> address.number is None
    True

...and the fields of subobjects (but not the subobject themselves!)::

    >>> json = '''
    ... {
    ...      "name": {
    ...       "first_name": null,
    ...       "last_name": null
    ...      },
    ...      "address": {
    ...       "street_name": null,
    ...       "number": null
    ...     }
    ... }
    ... '''
    >>> person = Person(Name('', ''), Address('', 0))
    >>> deserialize(json, IPerson, person)
    >>> person.name.first_name is None
    True
    >>> person.name.last_name is None
    True
    >>> IPerson.providedBy(person)
    True
    >>> IName.providedBy(person.name)
    True
    >>> person.address is None
    False
    >>> person.address.street_name is None
    True
    >>> person.address.number is None
    True
    >>> IAddress.providedBy(person.address)
    True

Similarly, empty sequences result in an empty list::

    >>> json = '''
    ... {
    ...   "members" : null
    ... }
    ... '''
    >>> commission = Commission([])
    >>> deserialize(json, ICommission, commission)
    >>> len(commission.members)
    0

Thus concludes the testing for TextLine, Int Object and List. We will now test other supported field types.

Datetime
========

Datetime objects::

    >>> from datetime import datetime
    >>> class IWithDatetime(interface.Interface):
    ...     datetime = schema.Datetime(title=u'Date and Time')
    >>> class WithDatetime(object):
    ...     implements(IWithDatetime)
    ...     def __init__(self, datetime):
    ...         self.datetime = datetime
    >>> with_datetime = WithDatetime(datetime(2008, 12, 31))
    >>> json = serialize(IWithDatetime, with_datetime)
    >>> print json
    {
       "datetime": "2008-12-31T00:00:00"
    }
    >>> new_datetime = WithDatetime(None)
    >>> deserialize(json, IWithDatetime, new_datetime)
    >>> new_datetime.datetime.year
    2008
    >>> new_datetime.datetime.month
    12
    >>> new_datetime.datetime.day
    31

Let's try it with the field not filled in::

    >>> with_datetime = WithDatetime(None)
    >>> json = serialize(IWithDatetime, with_datetime)
    >>> print json
    {
      "datetime": null
    }
    >>> new_datetime = WithDatetime(None)
    >>> deserialize(json, IWithDatetime, new_datetime)
    >>> new_datetime.datetime is None
    True

Choice
======

Choice fields. Currently, only Choice fields with text values are supported::

    >>> from zc.sourcefactory.basic import BasicSourceFactory
    >>> class ChoiceSource(BasicSourceFactory):
    ...     def getValues(self):
    ...         return [u'alpha', u'beta']
    >>> class IWithChoice(interface.Interface):
    ...     choice = schema.Choice(title=u'Choice', required=False,
    ...                           source=ChoiceSource())
    >>> class WithChoice(object):
    ...     implements(IWithChoice)
    ...     def __init__(self, choice):
    ...         self.choice = choice

Let's serialize a choice::

    >>> with_choice = WithChoice('alpha')
    >>> json = serialize(IWithChoice, with_choice)
    >>> print json
    {
      "choice": "alpha"
    }

And then deserialize it::

    >>> new_choice = WithChoice(None)
    >>> deserialize(json, IWithChoice, new_choice)
    >>> new_choice.choice
    'alpha'

Serializing empty choices::

    >>> with_choice = WithChoice(None)
    >>> json = serialize(IWithChoice, with_choice)
    >>> print json
    {
       "choice": null
    }

And then deserializing them::

    >>> deserialize(json, IWithChoice, new_choice)
    >>> new_choice.choice is None
    True

Set
===

Set fields are very similar to List fields::

    >>> class IWithSet(interface.Interface):
    ...     set = schema.Set(title=u'Set', required=False,
    ...                      value_type=schema.Choice(__name__='choice',
    ...                                               source=ChoiceSource()))
    >>> class WithSet(object):
    ...     implements(IWithSet)
    ...     def __init__(self, set):
    ...         self.set = set
    >>> with_set = WithSet(set(['alpha']))
    >>> json = serialize(IWithSet, with_set)
    >>> print json
    {
      "set": [
          "alpha"
      ]
    }
    >>> with_set = WithSet(set(['alpha', 'beta']))
    >>> json = serialize(IWithSet, with_set)
    >>> print json
    {
      "set": [
          "alpha",
          "beta"
      ]
    }
    >>> new_set = WithSet(None)
    >>> deserialize(json, IWithSet, new_set)
    >>> new_set.set
    set(['alpha', 'beta'])

Formatting
==========

The serializer allows both a human readible format and a compact
JSON representation to be produced. By default, the human readible
option is selected, but this may be overridden::

    >>> name = Name('Paul', 'Tom') 
    >>> print serialize(IName, name, pretty_print=False)
    {"first_name": "Paul", "last_name": "Tom"}
