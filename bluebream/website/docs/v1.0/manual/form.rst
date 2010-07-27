Forms
=====

Introduction
------------

BlueBream has a HTML form library called ``zope.formlib`` to generate
forms and widgets.  Instead of using a form library, you can create
all form manually.  But the formlib avoids many duplication works.
The formlib generate form for getting input data.  You can also
create validators and responses.

Forms are web components that use widgets to display and input data.
Typically a template displays the widgets by accessing an attribute
or method on an underlying class.  The form library has support for
validating user input data.  Form library automatically convert the
user submitted form data into Python objects.

The formlib provides some base classes for creating view classes.
The most used base classes are *DisplayForm*, *AddForm* and
*EditForm*.  The *DisplayForm* is not really a web form to submit,
but a convenience for displaying values based on particular
context/interface.

.. note::

  There is a popular community supported library called `z3c.form
  <http://docs.zope.org/z3c.form>`_ with more functionality &
  features compared to *zope.formlib*.  Many projects are using
  *z3c.form* library, and it is very well documented.

Concepts
--------

Before proceeding further let's look into some Form concepts.

Widget
~~~~~~

Formlib defines a widget like this: *views on bound schema fields*

Field
~~~~~

Fields build on schema fields.

Form
~~~~

A form class can define ordered collections of *form fields* using
the *Fields* constructor.  Form fields are distinct from and build on
schema fields.  A schema field specifies attribute values.  Form
fields specify how a schema field should be used in a form.  The
simplest way to define a collection of form fields is by passing a
schema to the *Fields* constructor.

Action
~~~~~~

Creating an AddForm
-------------------

The ``AddForm`` can be used as a base class for views.  It can be
imported like this::

  from zope.formlib.form import AddForm

A typical registration of view can be done like this::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="add_sample_app"
     permission="zope.ManageContent"
     class=".views.AddSampleApplication"
     />

You need a schema definition as explain in the previous chapter::

  class AddSampleApplication(form.AddForm):

      form_fields = form.Fields(ISampleApplication)

      def createAndAdd(self, data):
          name = data['name']
          description = data.get('description')
          namechooser = INameChooser(self.context)
          app = SampleApplication()
          name = namechooser.chooseName(name, app)
          app.name = name
          app.description = description
          self.context[name] = app
          self.request.response.redirect(name)


Creating an EditForm
--------------------

The usage of *EditForm* is very similar to *AddForm*.

Conclusion
----------

This chapter introduced *zope.formlib* library to generate HTML forms
and widgets.
