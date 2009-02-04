z3c.listjs
**********

z3c.listjs contains a widget called ``ListJsWidget`` that is a drop-in
replacement for the ``zope.app.form.browser.ListSequenceWidget``. It
allows users to add and remove list items without the need for server
interaction, using Javascript.

Note: This package only works with ``zope.formlib``
(``zope.app.form``) and is not compatible with ``z3c.form``.

You can use ``ListJsWidget`` for any ``schema.List`` field using the
normal ``zope.formlib`` custom widget pattern::
  
  from z3c.listjs import ListJsWidget

  ...

  form_fields['foo'].custom_widget = ListJsWidget

With the right ZCML override it should also be possible to
automatically use this widget in all cases ``ListSequenceWidget``
would normally be used. Documentation contributions are welcome!

Should you wish to override the CSS for the buttons, the CSS classes
are ``up_button`` and ``down_button``. If you are using hurry.resource
for your overriding CSS, your resource should depend on
``z3c.listjs.listjs_css`` so that ordering is correct to make the
override happen.
