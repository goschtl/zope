
.. contents::

``zope.httpform`` is a library that, given a WSGI or CGI environment
dictionary, will return a dictionary back containing converted
form/query string elements.  The form and query string elements
contained in the environment are converted into simple Python types when
the form element names are decorated with special suffixes.  For
example, in an HTML form that you'd like this library to process,
you might say::

  <form action=".">
     Age : <input type="hidden" name="age:int" value="20"/>
     <input type="submit" name="Submit"/>
  </form>

Likewise, in the query string of the URL, you could put::

   http://example.com/mypage?age:int=20

In both of these cases, when provided the WSGI or CGI environment,
and asked to return a value, this library will return a dictionary
like so::

  {'age':20}

This functionality has lived for a long time inside Zope, but now
Zope's publisher uses this library.

Form/Query String Element Parsing
---------------------------------

``zope.httpform`` provides a way for you to specify form input types in
the form, rather than in your application code. Instead of converting
the *age* variable to an integer in a controller or view, you can
indicate that it is an integer in the form itself::

       Age <input type="text" name="age:int" />

The ``:int`` appended to the form input name tells this library to
convert the form input to an integer when it is invoked.  If the
user of your form types something that cannot be converted to an
integer in the above case (such as "22 going on 23") then this library
will raise a ValueError.

Here is a list of the standard parameter converters.

``:boolean``

  Converts a variable to true or false.  Empty strings are evaluated as
  false and non-empty strings are evaluated as true.

``:int``

  Converts a variable to an integer.

``:long``

  Converts a variable to a long integer.

``:float``

  Converts a variable to a floating point number.

``:string``

  Converts a variable to a string.  Most variables are strings already,
  so this converter is not often used except to simplify file uploads.

``:text``

  Converts a variable to a string with normalized line breaks.
  Different browsers on various platforms encode line endings
  differently, so this script makes sure the line endings are
  consistent, regardless of how they were encoded by the browser.

``:list``

  Converts a variable to a Python list.

``:tuple``

  Converts a variable to a Python tuple.

``:tokens``

  Converts a string to a list by breaking it on white spaces.

``:lines``

  Converts a string to a list by breaking it on new lines.

``:required``

  Raises an exception if the variable is not present.

``:ignore_empty``

  Excludes the variable from the form data if the variable is an empty
  string.

These converters all work in more or less the same way to coerce a
form variable, which is a string, into another specific type.

The ``:list`` and ``:tuple`` converters can be used in combination with
other converters.  This allows you to apply additional converters to
each element of the list or tuple.  Consider this form::

       <form action=".">

         <p>I like the following numbers</p>

         <input type="checkbox" name="favorite_numbers:list:int"
         value="1" /> One<br />

         <input type="checkbox" name="favorite_numbers:list:int"
         value="2" />Two<br />

         <input type="checkbox" name="favorite_numbers:list:int"
         value="3" />Three<br />

         <input type="checkbox" name="favorite_numbers:list:int"
         value="4" />Four<br />

         <input type="checkbox" name="favorite_numbers:list:int"
         value="5" />5<br />

         <input type="submit" />
       </form>

By using the ``:list`` and ``:int`` converters together, this library
will convert each selected item to an integer and then combine all
selected integers into a list named *favorite_numbers*.

A more complex type of form conversion is to convert a series of
inputs into *records*. Records are structures that have
attributes. Using records, you can combine a number of form inputs
into one variable with attributes.  The available record converters
are:

``:record``

  Converts a variable to a record attribute.

``:records``

  Converts a variable to a record attribute in a list of records.

``:default``

  Provides a default value for a record attribute if the variable is
  empty.

``:ignore_empty``

  Skips a record attribute if the variable is empty.

Here are some examples of how these converters are used::

       <form action=".">

         First Name <input type="text" name="person.fname:record" /><br />
         Last Name <input type="text" name="person.lname:record" /><br />
         Age <input type="text" name="person.age:record:int" /><br />

         <input type="submit" />
       </form>

If the information represented by this form post is passed to
``zope.httpform``, the resulting dictionary will container one parameter,
*person*. The *person* variable will have the attributes *fname*,
*lname* and *age*. Here's an example of how you might use
``zope.httpform`` to process the form post (assuming you have a WSGI
or CGI environment in hand)::

  from zope.httpform import parse

  info = parse(environ, environ['wsgi.input'])
  person = info['person']
  full_name = "%s %s" % (person.fname, person.lname)
  if person.age < 21:
      return ("Sorry, %s. You are not old enough to adopt an "
              "aardvark." % full_name)
  return "Thanks, %s. Your aardvark is on its way." % full_name

The *records* converter works like the *record* converter except
that it produces a list of records, rather than just one. Here is
an example form::

  <form action=".">

    <p>Please, enter information about one or more of your next of
    kin.</p>

    <p>
      First Name <input type="text" name="people.fname:records" />
      Last Name <input type="text" name="people.lname:records" />
    </p>

    <p>
      First Name <input type="text" name="people.fname:records" />
      Last Name <input type="text" name="people.lname:records" />
    </p>

    <p>
      First Name <input type="text" name="people.fname:records" />
      Last Name <input type="text" name="people.lname:records" />
    </p>

    <input type="submit" />
  </form>

If you call ``zope.httpform``'s parse method with the information
from this form post, a dictionary will be returned from it with a
variable called *people* that is a list of records. Each record will
have *fname* and *lname* attributes.  Note the difference between the
*records* converter and the *list:record* converter: the former would
create a list of records, whereas the latter would produce a single
record whose attributes *fname* and *lname* would each be a list of
values.

The order of combined modifiers does not matter; for example,
``:int:list`` is identical to ``:list:int``.

Gotchas
-------

The file pointer passed to ``zope.httpform.parse()`` will be
consumed.  For all intents and purposes this means you should make a
tempfile copy of the ``wsgi.input`` file pointer before calling
``parse()`` if you intend to use the POST file input data in your
application.

Acknowledgements
----------------

This documentation was graciously donated by the team at
Agendaless Consulting.  The ``zope.httpform`` package is
expected to replace the ``repoze.monty`` package.
