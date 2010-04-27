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

The most used forms are DisplayForm, AddForm and EditForm.  The
DisplayForm is not really a web form to submit, but a convenience for
displaying values based on particular context/interface.

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

Conclusion
----------

This chapter introduced zope.formlib library to generate HTML forms
and widgets.
