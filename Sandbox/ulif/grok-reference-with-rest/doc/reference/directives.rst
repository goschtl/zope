
**********
Directives
**********

The :mod:`grok` module defines a set of directives that allow you to configure
and register your components. Most directives assume a default, based on the
environment of a module. (For example, a view will be automatically associated
with a model if the association can be made unambigously.)

If no default can be assumed for a value, grok will explicitly tell you what is
missing and how you can provide a default or explicit assignment for the value
in question.


:func:`grok.AutoFields` -- deduce schema fields automatically
=============================================================


.. function:: grok.AutoFields(class_or_interface)

   A class level directive, which can be used inside :class:`Form` classes to
   automatically deduce the form fields from the schema of the context
   `class_or_interface`.

   Different to most other directives, :func:`grok.AutoFields` is used more like a
   function and less like a pure declaration.

   The following example makes use of the :func:`grok.AutoFields` directive, in
   that one field is omitted from the form before rendering:

   **Example:** ::

      import grok
      from zope import interface, schema

      class IMammoth(interface.Interface):
          name = schema.TextLine(title=u"Name")
          size = schema.TextLine(title=u"Size", default=u"Quite normal")

      class Mammoth(grok.Model):
          interface.implements(IMammoth)

      class Edit(grok.EditForm):
          grok.context(Mammoth)

          form_fields = grok.AutoFields(Mammoth).omit('size')

   In this example the ``size`` attribute will not show up in the resulting edit
   view.


   .. seealso::

      :class:`grok.EditForm`, :class:`grok.Fields`


:func:`grok.adapts` -- declare that a class adapts certain objects
==================================================================


.. function:: grok.adapts(*classes_or_interfaces)

   A class-level directive to declare that a class adapts objects of the classes or
   interfaces given in `\*classes_or_interfaces`.

   This directive accepts several arguments.

   It works much like the :mod:`zope.component`\ s :func:`adapts()`, but you do not
   have to make a ZCML entry to register the adapter.

   **Example:** ::

      import grok
      from zope import interface, schema
      from zope.size.interfaces import ISized

      class IMammoth(interface.Interface):
          name = schema.TextLine(title=u"Name")
          size = schema.TextLine(title=u"Size", default=u"Quite normal")

      class Mammoth(grok.Model):
          interface.implements(IMammoth)

      class MammothSize(object):
          grok.implements(ISized)
          grok.adapts(IMammoth)

          def __init__(self, context):
              self.context = context

          def sizeForSorting(self):
              return ('byte', 1000)

          def sizeForDisplay(self):
              return ('1000 bytes')

   Having :class:`MammothSize` available, you can register it as an adapter,
   without a single line of ZCML::

      >>> manfred = Mammoth()
      >>> from zope.component import provideAdapter
      >>> provideAdapter(MammothSize)
      >>> from zope.size.interfaces import ISized
      >>> size = ISized(manfred)
      >>> size.sizeForDisplay()
      '1000 bytes'


   .. seealso::

      :class:`grok.implements`


:func:`grok.baseclass` -- declare a class as base
=================================================


.. function:: grok.baseclass()

   A class-level directive without argument to mark something as a base class. Base
   classes are are not grokked.

   Another way to indicate that something is a base class, is by postfixing the
   classname with ``'Base'``.

   The baseclass mark is not inherited by subclasses, so those subclasses will be
   grokked (except they are explicitly declared as baseclasses as well).

   **Example:** ::

      import grok

      class ModelBase(grok.Model):
          pass

      class ViewBase(grok.View):
          def render(self):
              return "hello world"

      class AnotherView(grok.View):
          grok.baseclass()

          def render(self):
              return "hello world"

      class WorkingView(grok.View):
          pass

   Using this example, only the :class:`WorkingView` will serve as a view, while
   calling the :class:`ViewBase` or :class:`AnotherView` will lead to a
   :exc:`ComponentLookupError`.


:func:`grok.define_permission` -- define a permission
=====================================================


.. function:: grok.define_permission(name)

   A module-level directive to define a permission with name `name`. Usually
   permission names are prefixed by a component- or application name and a dot to
   keep them unique.

   Because in Grok by default everything is accessible by everybody, it is
   important to define permissions, which restrict access to certain principals or
   roles.

   **Example:** ::

      import grok
      grok.define_permission('cave.enter')


   .. seealso::

      :func:`grok.require()`, :class:`grok.Permission`, :class:`grok.Role`

   .. versionchanged:: 0.11
      replaced by :class:`grok.Permission`.


:func:`grok.Fields`
===================


.. function:: grok.Fields(*arg)

   foobar


:func:`grok.implements`
=======================


.. function:: grok.implements(*arg)

   foobar


:func:`grok.context`
====================


.. function:: grok.context(*arg)

   foobar


:func:`grok.global_utility`
===========================


.. function:: grok.global_utility(*arg)

   foobar


:func:`grok.name`
=================


.. function:: grok.name(*arg)

   foobar

Used to associate a component with a name. Typically this directive is optional.
The default behaviour when no name is given depends on the component.


:func:`grok.local_utility`
==========================


.. function:: grok.local_utility(*arg)

   foobar


:func:`grok.provides`
=====================


.. function:: grok.provides(*arg)

   foobar


:func:`grok.resourcedir --- XXX Not implemented yet`
====================================================


.. function:: grok.resourcedir(*arg)

   foobar

Resource directories are used to embed static resources like HTML-, JavaScript-,
CSS- and other files in your application.

XXX insert directive description here (first: define the name, second: describe
the default behaviour if the directive isn't given)

A resource directory is created when a package contains a directory with the
name :file:`static`. All files from this directory become accessible from a
browser under the URL
:file:`http://<servername>/++resource++<packagename>/<filename>`.

**Example:** The package :mod:`a.b.c` is grokked and contains a directory
:file:`static` which contains the file :file:`example.css`. The stylesheet will
be available via :file:`http://<servername>/++resource++a.b.c/example.css`.

.. note::

   A package can never have both a :file:`static` directory and a Python module
   with the name :file:`static.py` at the same time. grok will remind you of this
   conflict when grokking a package by displaying an error message.


Linking to resources from templates
-----------------------------------

grok provides a convenient way to calculate the URLs to static resource using
the keyword :keyword:`static` in page templates::

   <link rel="stylesheet" tal:attributes="href static/example.css" type="text/css">

The keyword :keyword:`static` will be replaced by the reference to the resource
directory for the package in which the template was registered.


:func:`grok.require`
====================


.. function:: grok.require(*arg)

   foobar


:func:`grok.site`
=================


.. function:: grok.site(*arg)

   foobar


:func:`grok.template`
=====================


.. function:: grok.template(*arg)

   foobar


:func:`grok.templatedir`
========================


.. function:: grok.templatedir(*arg)

   foobar

