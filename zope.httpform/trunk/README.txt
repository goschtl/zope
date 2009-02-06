

This package provides a WSGI-oriented HTTP form parser with interesting
features to make form handling easier.  This functionality has lived
for a long time inside Zope's publisher, but has been broken out into
a separate package to make it easier to test, explain, understand, and use.

The parser uses Python's standard ``cgi.FieldStorage`` class, but is
easier to use than FieldStorage.  The parser converts field names and
values to Unicode, handles file uploads in a graceful manner, and allows
field name suffixes that tell the parser how to handle each field.
The available suffixes are:

    - ``:int``      -- convert to an integer
    - ``:float``    -- convert to a float
    - ``:long``     -- convert to a long integer
    - ``:string``   -- convert to a string instead of Unicode
    - ``:required`` -- raise ValueError if the field is not provided
    - ``:tokens``   -- split the input on whitespace characters
    - ``:lines``    -- split multiline input into a list of lines
    - ``:text``     -- convert multiline text to a string instead of Unicode
    - ``:boolean``  -- true if nonempty, false if empty
    - ``:list``     -- make a list even if there is only one value
    - ``:tuple``    -- make a tuple
    - ``:action``   -- specify the form action
    - ``:method``   -- same as ``:action``
    - ``:default``  -- provide a default value
    - ``:record``   -- generate a record object
    - ``:records``  -- generate a list of record object
    - ``:ignore_empty``   -- discard the field value if it's empty
    - ``:default_action`` -- specifies a default form action
    - ``:default_method`` -- same as ``:default_action``

Here are some examples of ways to use these suffixes.

* Using this package, you can provide a default for a field in an HTML form::

    <input type="text" name="country:ignore_empty" />
    <input type="hidden" name="country:default" value="Chile" />

  The form data returned by the parser will have a Unicode value for the
  ``country`` field, even if the user does not enter anything into the text box.

* You can ensure that certain variables are placed
  in a list, even when only one value is selected::

    <select name="cars:list" multiple="multiple">
    <option value="volvo">Volvo</option>
    <option value="saab">Saab</option>
    <option value="mercedes">Mercedes</option>
    <option value="audi">Audi</option>
    </select>

* You can group data into record objects, which is very useful for complex
  forms::

    <input type="text" name="shipping.name:record" />
    <input type="text" name="shipping.address:record" />
    <input type="text" name="shipping.phone:record" />
    <input type="text" name="billing.name:record" />
    <input type="text" name="billing.address:record" />
    <input type="text" name="billing.phone:record" />

You can do a lot more with these suffixes.  See
``src/zope/httpform/README.txt`` for a demonstration and test of all
features.
