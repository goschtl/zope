Forms
=====

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

Introduction
------------

BlueBream provides a HTML form library called ``zope.formlib`` to
generate forms and widgets.  There is an advanced community supported
library called ``z3c.form``.  This chapter will describe about using
``zope.formlib``.

Forms are web components that use widgets to display and input data.
Typically a template displays the widgets by accessing an attribute
or method on an underlying class.  BlueBream use ``zope.formlib`` to
create various forms.  Example form are AddForm, EditForm, Form.

Instead of using a form library, you can create all form manually.
But the formlib avoids many duplication works.  The formlib generate
form for getting input data.  You can also create validators and
responses.

Creating an AddForm
-------------------

Creating an EditForm
--------------------

Conclusion
----------

This chapter introduced zope.formlib library to generate HTML forms
and widgets.
