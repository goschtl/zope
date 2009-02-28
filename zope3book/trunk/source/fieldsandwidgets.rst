Custom Schema Fields and Form Widgets
=====================================

Introduction
------------

So far we have created fairly respectable content components and some
nice views for them.  Let's now look at the fine print; currently it
is possible that anything can be written into the message fields,
including malicious HTML and Javascript.  Therefore it would be
useful to develop a special field (and corresponding widget) that
strips out disallowed HTML tags.

Creating custom fields and widgets is a common task for end-user
applications, since these systems have often very specific
requirements.  It was a design goal of the schema/form sub-system to
be as customizable as possible, so it should be no surprise that it
is very easy to write your own field and widget.


Step I: Creating the Field
--------------------------

The goal of the special field should be to verify input based on
allowed or forbidden HTML tags.  If the message body contains HTML
tags other than the ones allowed or contains any forbidden tags, then
the validation of the value should fail.  Note that only one of the
two attributes can be specified at once.

It is often not necessary to write a field from scratch, since Zope 3
ships with a respectable collection already.  These serve commonly
also as base classes for custom fields.  For our HTML field the Text
field seems to be the most appropriate base, since it provides most
of the functionality for us already.

We will extend the Text field by two new attributes called
allowed_tags and forbidden_tags.  Then we are going to modify the
_validate() method to reflect the constraint made by the two new
attributes.


Interface
~~~~~~~~~

As always, the first step is to define the interface.  In the
messageboard's interfaces module, add the following lines::

  from zope.schema import Tuple
  from zope.schema.interfaces import IText
 
  class IHTML(IText):
      """A text field that handles HTML input."""
 
      allowed_tags = Tuple(
          title=u"Allowed HTML Tags",
          description=u"""\
           Only listed tags can be used in the value of the field.
           """,
           required=False)
 
       forbidden_tags = Tuple(
           title=u"Forbidden HTML Tags",
           description=u"""\
           Listed tags cannot be used in the value of the field.
           """,
           required=False)

- Line 1: The Tuple field simply requires a value to be a Python
  tuple.

- Line 2 & 4: We simple extend the IText interface and schema.

- Line 7-12 & 14-19: Define the two additional attributes using the
  field Tuple.


Implementation
~~~~~~~~~~~~~~

As previously mentioned, we will use the Text field as base class,
since it provides most of the functionality we need.  The main task
of the implementation is to rewrite the validation method.

Let's start by editing a file called fields.py in the messageboard
package and inserting the following code::

  import re
 
  from zope.schema import Text
  from zope.schema.interfaces import ValidationError
 
  forbidden_regex = r'</?(?:%s).*?/?>'
  allowed_regex = r'</??(?!%s[ />])[a-zA-Z0-9]*?
   ?(?:[a-z0-9]*?=?".*?")*/??>'
 
  class ForbiddenTags(ValidationError):
       __doc__ = u"""Forbidden HTML Tags used."""
 
 
   class HTML(Text):
 
       allowed_tags = ()
       forbidden_tags = ()
 
       def __init__(self, allowed_tags=(), forbidden_tags=(), **kw):
           self.allowed_tags = allowed_tags
           self.forbidden_tags = forbidden_tags
           super(HTML, self).__init__(**kw)
 
       def _validate(self, value):
           super(HTML, self)._validate(value)
 
           if self.forbidden_tags:
               regex = forbidden_regex %'|'.join(self.forbidden_tags)
               if re.findall(regex, value):
                   raise ForbiddenTags(value, self.forbidden_tags)
 
           if self.allowed_tags:
               regex = allowed_regex %'[ />]|'.join(self.allowed_tags)
               if re.findall(regex, value):
                   raise ForbiddenTags(value, self.allowed_tags)

- Line 1: Import the Regular Expression module ( re); we will use
  regular expressions to do the validation of the HTML.

- Line 3: Import the Text field that we will use as base class for
  the HTML field.

- Line 4 & 10-11: The validation method of the new HTML field will be
  able to throw a new type of validation error when an illegal HTML
  tag is found.

  Usually errors are defined in the interfaces module, but since it
  would cause a recursive import between the interfaces and fields
  module, we define it here.

- Line 7-9: These strings define the regular expression templates for
  detecting forbidden or allowed HTML tags, respectively.  Note that
  these regular expressions are quiet more restrictive than what the
  HTML 4.01 standard requires, but it is good enough as
  demonstration.  See exercise 1 at the end of the chapter to see how
  it should be done correctly.

- Line 16-19: In the constructor we are extracting the two new
  arguments and send the rest to the constructor of the Text field
  (line 21).

- Line 22: First we delegate validation to the Text field.  The
  validation process might already fail at this point, so that
  further validation becomes unnecessary.

- Line 24-27: If forbidden tags were specified, then we try to detect
  them.  If one is found, a ForbiddenTags error is raised attaching
  the faulty value and the tuple of forbidden tags to the exception.

- Line 29-32: Similarly to the previous block, this block checks that
  all used tags are in the collection of allowed_tags otherwise a
  ForbiddenTags error is raised.

We have an HTML field, but it does not implement IHTML interface.
Why not? It is due to the fact that it would cause a recursive import
once we use the HTML field in our content objects.  To make the
interface assertion, add the following lines to the interfaces.py
module:


  from zope.interface import classImplements
  from fields import HTML
  classImplements(HTML, IHTML)

At this point we should have a working field, but let's write some
unit tests to verify the implementation.


Unit Tests
~~~~~~~~~~

Since we will use the Text field as a base class, we can also reuse
the Text field's tests.  Other than that, we simply have to test the
new validation behavior.

In messageboard/tests add a file test_fields.py and add the following
base tests.  Note that the code is not complete (abbreviated sections
are marked by ...).  You can find it in the source repository though.

::

  import unittest
  from zope.schema.tests.test_strfield import TextTest
 
  from book.messageboard.fields import HTML, ForbiddenTags
 
  class HTMLTest(TextTest):
 
      _Field_Factory = HTML
 
       def test_AllowedTagsHTMLValidate(self):
           html = self._Field_Factory(allowed_tags=('h1','pre'))
           html.validate(u'<h1>Blah</h1>')
           ...
           self.assertRaises(ForbiddenTags, html.validate,
                             u'<h2>Foo</h2>')
           ...
 
       def test_ForbiddenTagsHTMLValidate(self):
           html = self._Field_Factory(forbidden_tags=('h2','pre'))
           html.validate(u'<h1>Blah</h1>')
           ...
           self.assertRaises(ForbiddenTags, html.validate,
                             u'<h2>Foo</h2>')
           ...
 
   def test_suite():
       return unittest.TestSuite((
           unittest.makeSuite(HTMLTest),
           ))
 
   if __name__ == '__main__':
       unittest.main(defaultTest='test_suite')

- Line 2: Since we use the Text field as base class, we can also use
  it's test case as base, getting some freebie tests in return.

- Line 8: However, the TextTest base comes with some rules we have to
  abide to.  Specifying this _Field_Factory attribute is required, so
  that the correct field is tested.

- Line 10-16: These are tests of the validation method using the
  allowed tags attribute.  Some text was removed some to conserve
  space.  You can look at the code for the full test suite.

- Line 18-24: Here we are testing the validation method using the
  forbidden_tags attribute.


Step II: Creating the Widget
----------------------------

Widgets are simply views of a field.  Therefore we place the widget
code in the browser sub-package.

Our HTMLSourceWidget will use the TextAreaWidget as a base and only
the converter method _convert(value) has to be reimplemented, so that
it will remove any undesired tags from the input value (yes, this
means that the validation of values coming through these widgets will
always pass.)


Implementation
~~~~~~~~~~~~~~

Since there is no need to create a new interface, we can start right
away with the implementation.  We get started by adding a file called
widgets.py and inserting the following content::

  import re
  from zope.app.form.browser import TextAreaWidget
  from book.messageboard.fields import forbidden_regex, allowed_regex
 
  class HTMLSourceWidget(TextAreaWidget):
 
    def _toFieldValue(self, input):
        input = super(HTMLSourceWidget, self)._toFieldValue(input)
 
         if self.context.forbidden_tags:
             regex = forbidden_regex %'|'.join(
                 self.context.forbidden_tags)
             input = re.sub(regex, '', input)
 
         if self.context.allowed_tags:
             regex = allowed_regex %'[ />]|'.join(
                 self.context.allowed_tags)
             input = re.sub(regex, '', input)
 
         return input

- Line 2: As mentioned above, we are going to use the TextAreaWidget
  as a base class.

- Line 3: There is no need to redefine the regular expressions for
  finding forbidden and non-allowed tags again, so we use the field's
  definitions.  This will also avoid that the widget converter and
  field validator get out of sync.

- Line 8: We still want to use the original conversion, since it
  takes care of weird line endings and some other routine cleanups.

- Line 10-13: If we find a forbidden tag, simply remove it by
  replacing it with an empty string.  Notice how we get the
  forbidden_tags attribute from the context (which is the field
  itself) of the widget.

- Line 15-18: If we find a tag that is not in the allowed tags tuple,
  then remove it as well.

Overall, this a very nice and compact way of converting the input
value.


Unit Tests
~~~~~~~~~~

While we usually do not write unit tests for high-level view code,
widget code should be tested, particularly the converter.  Open
test_widgets.py in browser/tests and insert::

  import unittest
  from zope.app.form.browser.tests.test_textareawidget import
   TextAreaWidgetTest
  from book.messageboard.browser.widgets import HTMLSourceWidget
  from book.messageboard.fields import HTML
 
  class HTMLSourceWidgetTest(TextAreaWidgetTest):
 
      _FieldFactory = HTML
      _WidgetFactory = HTMLSourceWidget
 
 
       def test_AllowedTagsConvert(self):
           widget = self._widget
           widget.context.allowed_tags=('h1','pre')
           self.assertEqual(u'<h1>Blah</h1>',
                            widget._toFieldValue(u'<h1>Blah</h1>'))
           ...
           self.assertEqual(u'Blah',
                            widget._toFieldValue(u'<h2>Blah</h2>'))
           ...
 
       def test_ForbiddenTagsConvert(self):
           widget = self._widget
           widget.context.forbidden_tags=('h2','pre')
 
           self.assertEqual(u'<h1>Blah</h1>',
                            widget._toFieldValue(u'<h1>Blah</h1>'))
           ...
           self.assertEqual(u'Blah',
                            widget._toFieldValue(u'<h2>Blah</h2>'))
           ...
 
   def test_suite():
       return unittest.TestSuite((
           unittest.makeSuite(HTMLSourceWidgetTest),
           ))
 
   if __name__ == '__main__':
       unittest.main(defaultTest='test_suite')

- Line 2: Of course we are reusing the TextAreaWidgetTest to get some
  freebie tests.

- Line 8-9: Fulfilling the requirements of the TextAreaWidgetTest, we
  need to specify the field and widget we are using, which makes
  sense, since the widget must have the field (context) in order to
  fulfill all its duties.

- Line 12-31: Similar in nature to the field tests, the converter is
  tested.  In this case however, we compare the output, since it can
  differ from the input based on whether forbidden tags were found or
  not.


Step III: Using the HTML Field
------------------------------

Now we have all the pieces we need.  All that's left is to integrate
them with the rest of the package.  There are a couple of steps
involved.  First we register the HTMLSourceWidget as a widget for the
HTML field.  Next we need to change the IMessage interface
declaration to use the HTML field.


Registering the Widget
~~~~~~~~~~~~~~~~~~~~~~

To register the new widget as a view for the HTML field we use the
zope namespace view directive.  Therefore you have to add the zope
namespace to the configuration file's namespace list by adding the
following line int he opening configure element::


  xmlns:zope="http://namespaces.zope.org/zope"

Now add the following directive::


  <zope:view
      type="zope.publisher.interfaces.browser.IBrowserRequest"
      for="book.messageboard.interfaces.IHTML"
      provides="zope.app.form.interfaces.IInputWidget"
      factory=".widgets.HTMLSourceWidget"
      permission="zope.Public"
      />

- Line 2: Since the zope:view directive can be used for any
  presentation type (for example: HTTP, WebDAV and FTP), it is
  necessary to state that the registered widget is for browsers
  (i.e. HTML).

- Line 3: This widget will work for all fields implementing IHTML.

- Line 4: In general presentation component, like adapters, can have
  a specific output interface.  Usually this interface is just
  zope.interface.  Interface, but here we specifically want to say
  that this is a widget that is accepting input for the field.  The
  other type of widget is the DisplayWidget.

- Line 5: Specifies the factory or class that will be used to
  generate the widget.

- Line 6: We make this widget publically available, meaning that
  everyone using the system can use the widget as well.


Adjusting the IMessage interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The final step is to use the field in the IMessage interface.  Let's
go to the interfaces module to decide which property is going to
become an HTML field.  The field is already imported.

Now, we definitely want to make the body property of IMessage an HTML
field.  We could also do this for description of IMessageBoard, but
let's not to do that for reasons of keeping it simple.  So here are
the changes that need to be done to the body property declaration
(starting at line 24)::


  body = HTML(
      title=u"Message Body",
      description=u"This is the actual message. Type whatever!",
      default=u"",
      allowed_tags=('h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'a',
                    'br', 'b', 'i', 'u', 'em', 'sub', 'sup',
                    'table', 'tr', 'td', 'th', 'code', 'pre',
                    'center', 'div', 'span', 'p', 'font', 'ol',
                    'ul', 'li', 'q', 's', 'strong'),
       required=False)

- Line 5-9: Here is our new attribute that was added in the IHTML
  interface.  This is my choice of valid tags, so feel free to add or
  remove whatever tags you like.

And that's it! You are done.  To try the result of your work, restart
Zope 3, start editing a new message and see if it will accept tags
like html or body.  You should notice that these tags will be
silently removed from the message body upon saving it.


Exercises
---------

1. Instead of using our own premature HTML cleanup facilities, we
   really should make use of Chris Wither's HTML Strip-o-Gram package
   which can be found at
   `http://www.zope.org/Members/chrisw/StripOGram`_. Implement a
   version of the HTML field and HTMLSourceWidget widget using this
   package.

2. Sometimes it might be nice to also allow HTML for the title of the
   messages, therefore you will also need an HTML version for the
   TextLine field and the TextWidget. Abstract the current converter
   and validation implementation, so that it is usable for both,
   message title and body.

3. Using only HTML as input can be boring and tedious for some
   message board applications. In the zwiki for Zope 3 packge we make
   use of a system ( zope.app.renderer) that let's you select the
   type of input and then knows how to render each type of input for
   the browser. Insert this type of system into the message board
   application and merge it with the HTML validation and conversion
   code.

.. _http://www.zope.org/Members/chrisw/StripOGram:
    http://www.zope.org/Members/chrisw/StripOGram
