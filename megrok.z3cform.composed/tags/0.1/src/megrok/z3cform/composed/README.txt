=======================
megrok.z3cform.composed
=======================

`megrok.z3cform.composed` is a package dedicated to define and
register composed forms. Composed forms are forms built from a
collection of sub forms.

`megrok.z3cform.composed` is based on `z3c.form` and
`megrok.z3cform.base`.


Getting started
===============

We import the needed dependencies::

  >>> import grokcore.view as grok
  >>> import megrok.z3cform.composed
  >>> from megrok.z3cform.composed import ComposedForm, SubForm

We import the components utilities::

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest


Defining a composed form
========================

Context
-------

A form needs a context. Let's create a simple model for test purposes::

  >>> class MyContent(object):
  ...    pass


Declaration
-----------

  >>> class Form(ComposedForm):
  ...   grok.context(MyContent)


Registration
------------

  >>> grok_component('composed', Form)
  True


Query
-----

  >>> content = MyContent()
  >>> request = TestRequest()

  >>> composed = getMultiAdapter((content, request), name="form")
  >>> composed
  <megrok.z3cform.composed.tests.Form object at ...>

  >>> composed.subforms
  []

  >>> composed.updateForm()
  >>> composed.subforms
  []


Defining sub forms
==================

Declaration
-----------

  >>> class SubFormOne(SubForm):
  ...     grok.context(MyContent)
  ...     megrok.z3cform.composed.order(2)
  ...     megrok.z3cform.composed.view(Form)

  >>> class SubFormTwo(SubForm):
  ...     grok.context(MyContent)
  ...     megrok.z3cform.composed.order(1)
  ...     megrok.z3cform.composed.view(Form)


Registration
------------

  >>> grok_component('one', SubFormOne)
  True

  >>> grok_component('one', SubFormTwo)
  True


Query
-----

  >>> composed.subforms
  []

  >>> composed.updateForm()
  >>> composed.subforms
  [<megrok.z3cform.composed.tests.SubFormTwo object at ...>, <megrok.z3cform.composed.tests.SubFormOne object at ...>]

  >>> for sub in composed.subforms:
  ...   print sub.prefix, sub.parentForm
  subformtwo <megrok.z3cform.composed.tests.Form object at ...>
  subformone <megrok.z3cform.composed.tests.Form object at ...>
