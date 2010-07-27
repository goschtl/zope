Schemas and Widgets
===================

.. highlight:: python
   :linenothreshold: 5

Introduction
------------

In the early stages of development, the BlueBream (then know as Zope
3) developers decided that it would be cumbersome to manually write
HTML forms and to manually validate the input.  BlueBream team
realized that if they could extend interfaces, we could auto-generate
HTML forms and also automatically validate any input.  This chapter
gives some background information and formally introduces the
``zope.schema`` and ``zope.formlib`` packages.

Schema is an interface defined using special attributes called
``fields``.

The schema was developed based on the following three main goals:

1.  Full specification of properties on an API level

2.  Data input validation and conversion

3.  Automated GUI form generation (mainly for the Web browser)


Schema versus Interfaces
------------------------

As mentioned before, schemas are just an extension to interfaces and
therefore depend on the *zope.interface* package.  Fields in schemas
are equivalent to methods in interfaces.  Both are complementary to
each other, since they describe different aspects of an object.  The
methods of an interface describe the functionality of a component,
while the schema's fields represent the state.

It is thus not necessary to develop a new syntax for writing schemas
so, schema simply reuse the interface declaration.

::

  from zope.interface import Interface
  from zope.schema import Text

  class IExample(Interface):

      text = Text(
          title=u"Text",
          description=u"The text of the example.",
          required=True)

- Line 2: All default fields can be simply imported from
  ``zope.schema``.

- Line 7-8: The title and description are used as human-readable text
  for the form generation. Of course, they also serve as
  documentation of the field itself.

- Line 9: Various fields support several other meta-data fields.  The
  required option is actually available for all fields and specifies
  whether an object implementing IExample must provide a value for
  text or not.


Core Schema Fields
------------------

After we have seen a simple example of a schema, let's now look at
all the basic fields and their properties.

- Properties that all fields support:

  - ``title`` (type: *TextLine*): The title of the attribute is used
    as label when displaying the field widget.

  - ``description`` (type: *Text*): The description of the attribute
    is used for tooltips and advanced help.

  - ``required`` (type: *Bool*): Specifies whether an attribute is
    required or not to have a value.  In add-forms, required
    attributes are equivalent to required constructor arguments.

  - ``readonly`` (type: *Bool*): If a field is readonly, then the
    value of the attribute can be set only once and can then only be
    displayed.  Often a unique id for some object is a good candidate
    for a read-only field.

  - ``default`` (type: depends on field): The default value that is
    given to the attribute, if no initialization value was provided.
    This value is often specified, if a field is required.

  - ``order`` (type: *Int*): Fields are often grouped by some logical
    order.  This value specifies a relative position in this order.
    We usually do not set this value manually, since it is
    automatically assigned when an interface is initialized.  The
    order of the fields in a schema is by default the same as the
    order of the fields in the Python code.

- Bytes, BytesLine

  Bytes and BytesLine only differ by the fact that BytesLine cannot
  contain a new line character.  Bytes behave identical to the Python
  type str.

  Bytes and BytesLine fields are iteratable.

  - ``min_length`` (type: *Int*): After the white space has been
    normalized, there cannot be less than this amount of characters
    in the bytes string.  The default is None, which refers to no
    minimum.

  - ``max_length`` (type: *Int*): After the white space has been
    normalized, there cannot be more than this amount of characters
    in the bytes string.  The default is None, which refers to no
    maximum.

- Text, TextLine

  The two fields only differ by the fact that TextLine cannot contain
  a newline character.  Text fields contain unicode, meaning that
  they are intended to be human-readable strings/text.

  Text and TextLine fields are iteratable.

  - ``min_length`` (type: *Int*): After the white space has been
    normalized, there cannot be less than this amount of characters
    in the text string.  The default is None, which refers to no
    minimum.

  - ``max_length`` (type: *Int*): After the white space has been
    normalized, there cannot be more than this amount of characters
    in the text string.  The default is None, which refers to no
    maximum.

- SourceText

  Source Text is a special field derived from Text, which contains
  source code of any type.  It is more or less a marker field for the
  forms machinery, so that special input fields can be used for
  source code.

- Password

  Password is a special derivative for the TextLine field and is
  treated separately for presentation reasons.  However, someone also
  might want more fine-grained validation for passwords.

- Bool

  The Bool field has no further attributes.  It maps directly to
  Python's bool object.

- Int

  Int fields directly map to Python's int type.

  - ``min`` (type: *Int*): Specifies the smallest acceptable integer.
    This is useful in many ways, such as allowing only positive
    values by making this field 0.

  - ``max`` (type: *Int*): Specifies the largest acceptable integer,
    which excludes the value itself.  It can be used to specify an
    upper bound, such as the current year, if you are interested in
    the past only.

  Both attributes combined allow the programmer to specify ranges of
  acceptable values.

- Float

  Float fields directly map to Python's float type.

  - ``min`` (type: *Float*): Specifies the smallest acceptable
    floating point number.  This is useful in many ways, such as
    allowing only positive values by making this field 0.0.

  - ``max`` (type: *Float*): Specifies the largest acceptable
    floating point number, which excludes the value itself (typical
    computer programming pattern).  It can be used to specify an
    upper bound, such as 1.0, if you are only interested in
    probabilities.

  Both attributes combined allow the programmer to specify ranges of
  acceptable values.

- Datetime

  Similar to Int and Float, Datetime has a min and max field that
  specify the boundaries of the possible values.  Acceptable values
  for these fields must be instances of the builtin datetime type.

- Tuple, List

  The reason both of these fields exists is that we can easily map
  them to their Python type tuple and list, respectively.

  Tuple and List fields are iteratable.

  - ``min_length`` (type: *Int*): There cannot be less than this
    amount of items in the sequence.  The default is None, which
    means there is no minimum.

  - ``max_length`` (type: *Int*): There cannot be more than this
    amount of items in the sequence.  The default is None, which
    means there is no maximum.

  - ``value_type`` (type: *Field*): Values contained by these
    sequence types must conform to this field's constraint.  Most
    commonly a Choice field (see below) is specified here, which
    allows you to select from a fixed set of values.

- Dict

  The Dict is a mapping field that maps from one set of fields to
  another.

  fields are iteratable.

  - ``min_length`` (type: *Int*): There cannot be less than this
    amount of items in the dictionary.  The default is None, which
    means there is no minimum.

  - ``max_length`` (type: *Int*): There cannot be more than this
    amount of items in the dictionary.  The default is None, which
    means there is no maximum.

  - ``key_type`` (type: *Field*): Every dictionary item key has to
    conform to the specified field.

  - ``value_type`` (type: *Field*): Every dictionary item value has
    to conform to the specified field.

- Choice

  The Choice field allows one to select a particular value from a
  provided set of values.  You can either provide the values as a
  simple sequence (list or tuple) or specify a vocabulary (by
  reference or name) that will provide the values.  Vocabularies
  provide a flexible list of values, in other words the set of
  allowed values can change as the system changes.  Since they are so
  complex, they are covered separately in "Vocabularies and Fields".

  - ``vocabulary`` (type: *Vocabulary*): A vocabulary instance that
    is used to provide the available values.  This attribute is None,
    if a vocabulary name was specified and the field has not been
    bound to a context.

  - ``vocabularyName`` (type: *TextLine*): The name of the vocabulary
    that is used to provide the values.  The vocabulary for this name
    can only be looked up, when the field is bound, in other words
    has a context.  Upon binding, the vocabulary is automatically
    looked using the name and the context.

  The constructor also accepts a values argument that specifies a
  static set of values.  These values are immediately converted to a
  static vocabulary.

- Object

  This field specifies an object that must implement a specific
  schema.  Only objects that provide the specified schema are
  allowed.

  - ``schema`` (type: *Interface*): This field provides a reference
    to the schema that must be provided by objects that want to be
    stored in the described attribute.

- DottedName

  Derived from the BytesLine field, the DottedName field represents
  valid Python-style dotted names (object references).  This field
  can be used when it is desirable that a valid and resolvable Python
  dotted name is provided.

  This field has no further attributes.

- URI

  Derived from the BytesLine field, the URI field makes sure that the
  value is always a valid URI.  This is particularly useful when you
  want to reference resources (such as RSS feeds or images) on remote
  computers.

  This field has no further attributes.

- Id

  Both, the DottedName and URI field, make up the Id field.  Any
  dotted name or URI represent a valid id in Zope.  Ids are used for
  identifying many types of objects, such as permissions and
  principals, but also for providing annotation keys.

  This field has no further attributes.

- InterfaceField

  The Interface field has no further attributes.  Its value must be
  an object that provides zope.interface.Interface, in other words it
  must be an interface.

For a formal listing of the Schema/Field API, see the API
documentation tool at `http://localhost:8080/++apidoc++`_ or see
zope.schema.interfaces module.


Auto-generated Forms using the forms Package
--------------------------------------------

Forms are much more BlueBream specific than schemas and can be found
in the ``zope.formlib`` package.  The views of schema fields are
called widgets.  Widgets responsible for data display and conversion
in their specific presentation type.  Currently widgets exist mainly
for HTML (the Web browser).

Widgets are separated into two groups, display and input widgets.
Display widgets are often very simply and only show a text
representation of the Python object.  The input widgets, however, are
more complex and display a greater variety of choices.  The following
list shows all available browser- based input widgets (found in
zope.formlib.widget):


Text Widgets
~~~~~~~~~~~~

Text-based widgets always require some sort of keyboard input.  A
string representation of a field is then converted to the desired
Python object, like and integer or a date.

- ``TextWidget``: Being probably the simplest widget, it displays the
  text input element and is mainly used for the ``TextLine``, which
  expects to be unicode.  It also serves as base widget for many of
  the following widgets.

- ``TextAreaWidget``: As the name suggests this widget displays a
  text area and assumes its input to be some unicode string.  (note
  that the Publisher already takes care of the encoding issues).

- ``BytesWidget``, ``BytesAreaWidget``: Direct descendents from
  ``TextWidget`` and ``TextAreaWidget``, the only difference is that
  these widgets expect bytes as input and not a unicode string, which
  means they must be valid ASCII encodable.

- ``ASCIIWidget``: This widget, based on the ``BytesWidget``, ensures
  that only ASCII character are part of the inputted data.

- ``PasswordWidget``: Almost identical to the ``TextWidget``, it only
  displays a password element instead of a text element.

- ``IntWidget``: A derivative of ``TextWidget``, it only overwrites
  the conversion method to ensure the conversion to an integer.

- ``FloatWidget``: Derivative of ``TextWidget``, it only overwrites
  the conversion method to ensure the conversion to an floating
  point.

- ``DatetimeWidget``: Someone might expect a smart and complex widget
  at this point, but for now it is just a simple ``TextWidget`` with
  a string to datetime converter.  There is also a ``DateWidget``
  that only handles dates.

Boolean Widgets
~~~~~~~~~~~~~~~

Boolean widgets' only responsibility is to convert some binary input
to the Python values *True* or *False*.

- ``CheckBoxWidget``: This widget displays a single checkbox widget
  that can be either checked or unchecked, representing the state of
  the boolean value.

- ``BooleanRadioWidget``: Two radio buttons are used to represent the
  true and false state of the boolean.  One can pass the textual
  value for the two states in the constructor.  The default is *on*
  and *off* (or their translation for languages other than English).

- ``BooleanSelectWidget``, ``BooleanDropdownWidget``: Similar to the
  ``BooleanRadioWidget``, textual representations of the true and
  false state are used to select the value.  See ``SelectWidget`` and
  ``DropdownWidget``, respectively, for more details.


Single Selection Widgets
~~~~~~~~~~~~~~~~~~~~~~~~

Widgets that allow a single item to be selected from a list of values
are usually views of a field, a vocabulary and the request, instead
of just the field and request pair.  Therefore so called
proxy-widgets are used to map from field-request to
field-vocabulary-request pairs.  For example the
``ChoiceInputWidget``, which takes a Choice field and a request
object, is simply a function that looks up another widget that is
registered for the Choice field, its vocabulary and the request.
Below is a list of all available widgets that require the latter
three inputs.

- ``SelectWidget``: This widget provides a multiply-sized selection
  element where the options are populated through the vocabulary
  terms.  If the field is not required, a "no value" option will be
  available as well.  The user will allowed to only select one value
  though, since the ``Choice`` field is not a sequence-based field.

- ``DropdownWidget``: As a simple derivative of the ``SelectWdiget``,
  it has its size set to "1", which makes it a dropdown box.
  Dropdown boxes have the advantage that they always just show one
  value, which makes some more user-friendly for single selections.

- ``RadioWidget``: This widget displays a radio button for each term
  in the vocabulary.  Radio buttons have the advantage that they
  always show all choices and are therefore well suitable for small
  vocabularies.


Multiple Selections Widgets
~~~~~~~~~~~~~~~~~~~~~~~~~~~

This group of widgets is used to display input forms collection-based
fields, such as List or Set.  Similar to the single selection
widgets, two proxy- widgets are used to look up the correct widget.
The first step is to map from field- request to field- value_type-
request using a widget called ``CollectionInputWidget``.  This allows
us to use different widgets when the value type is an Int or Choice
field for example.  Optionally, a second proxy-widget is used to
convert the field- value_type- request pair to a field- vocabulary-
request pair, as it is the case when the value type is a choice
field.

- ``MultiSelectWidget``: Creates a select element with the multiple
  attribute set to true.  This creates a multi-selection box.  This
  is especially useful for vocabularies with many terms.  Note that
  if your vocabulary supports a query interface, you can even filter
  your selectable items using queries.

- ``MultiCheckBoxWidget``: Similar to the multi-selection widget,
  this widget allows multi-value selections of a given list, but uses
  checkboxes instead of a list.  This widget is more useful for
  smaller vocabularies.

- ``TupleSequenceWidget``: This widget is used for all cases where
  the value type is not a Choice field.  It used the widget of the
  value type field to add new values to the tuple.  Other input
  elements are used to remove items.

- ``ListSequenceWidget``: This widget is equivalent to the previous
  one, except that it generates lists instead of tuples.


Miscellaneous Widgets
~~~~~~~~~~~~~~~~~~~~~

- ``FileWidget``: This widget displays a file input element and makes
  sure the received data is a file.  This field is ideal for quickly
  uploading byte streams as required for the ``Bytes`` field.

- ``ObjectWidget``: The ``ObjectWidget`` is the view for an object
  field.  It uses the schema of the object to construct an input
  form.  The object factory, which is passed in as a constructor
  argument, is used to build the object from the input afterwards.

Here is a simple interactive example demonstrating the rendering and
conversion functionality of a widget::

  >>> from zope.publisher.browser import TestRequest
  >>> from zope.schema import Int
  >>> from zope.formlib.widget import IntWidget
  >>> field = Int(__name__='number', title=u'Number', min=0, max=10)
  >>> request = TestRequest(form={'field.number': u'9'})
  >>> widget = IntWidget(field, request)
  >>> widget.hasInput()
  True
  >>> widget.getInputValue()
   9
  >>> print widget().replace(' ', '\n  ')
  <input
     class="textType"
     id="field.number"
     name="field.number"
     size="10"
     type="text"
     value="9"
 
  />

- Line 1 & 5: For views, including widgets, we always need a request
  object.  The ``TestRequest`` class is the quick and easy way to
  create a request without much hassle.  For each presentation type
  there exists a TestRequest class.  The class takes a form argument,
  which is a dictionary of values contained in the HTML form.  The
  widget will later access this information.

- Line 2: Import an integer field.

- Line 3 & 6: Import the widget that displays and converts an integer
  from the HTML form.  Initializing a widget only requires a field
  and a request.

- Line 4: Create an integer field with the constraint that the value
  must lie between 0 and 10.  The __name__ argument must be passed
  here, since the field has not been initialized inside an interface,
  where the __name__ would be automatically assigned.

- Line 7-8: This method checks whether the form contained a value for
  this widget.

- Line 9-10: If so, then we can use the ``getInputValue()`` method to
  return the converted and validated value (an integer in this case).
  If we would have chosen an integer outside this range, a
  WidgetInputError would have been raised.

- Line 11-20: Display the HTML representation of the widget.  The
  ``replace()`` call is only for better readability of the output.

Note that you usually will not have to deal with these methods at all
manually, since the form generator and data converter does all the
work for you.  The only method you will commonly overwrite is
``_validate()``, which you will use to validate custom values.  This
brings us right into the next subject, customizing widgets.

There are two ways of customizing widgets.  For small adjustments to
some parameters (properties of the widget), one can use the
browser:widget subdirective of the browser:addform and
browser:editform directives.  For example, to change the widget for a
field called "name", the following ZCML code can be used.

::

  <browser:addform
    ... >
 
    <browser:widget
        field="name"
        class="zope.formlib.widget.TextWidget"
        displayWidth="45"
        style="width: 100%"/>
 
  </browser:addform>

In this case we force the system to use the ``TextWidget`` for the
name, set the display width to 45 characters and add a style
attribute that should try to set the width of the input box to the
available width.

The second possibility to change the widget of a field is to write a
custom view class.  In there, custom widgets are easily realized
using the CustomWidget wrapper class.  Here is a brief example::

  from zope.formlib.widget import CustomWidget
  from zope.formlib.widget import TextWidget

  class CustomTextWidget(TextWidget):
      ...

  class SomeView:
      name_widget = CustomWidget(CustomTextWidget)

- Line 1: Since ``CustomWidget`` is presentation type independent, it
  is defined in ``zope.app.form.widget``.

- Line 4-5: You simply extend an existing widget.  Here you can
  overwrite everything, including the ``_validate()`` method.

- Line 7-8: You can hook in the custom widget by adding an attribute
  called name_widget, where name is the name of the field.  The value
  of the attribute is a ``CustomWidget`` instance.  ``CustomWidget``
  has only one required constructor argument, which is the custom
  widget for the field.  Other keyword arguments can be specified as
  well, which will be set as attributes on the widget.

More information about schemas can be found in the README.txt file of
the ``zope.schema`` package.

This concludes our introduction to schemas and forms.  For examples
of schemas and forms in practice, see the tutorial.

.. _http://localhost:8080/++apidoc++: http://localhost:8080/++apidoc++
