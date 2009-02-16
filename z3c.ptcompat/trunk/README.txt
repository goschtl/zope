Overview
========

This package implements a compatibility-layer between the following
Zope Page Template engines:

 * z3c.pt
 * zope.pagetemplate

If the environment-variable ``PREFER_Z3C_PT`` is set to a true value,
the ``z3c.pt`` engine will be used instead of ``zope.pagetemplate``.

Note: This package superseeds and replaces the old z3c.pt.compat,
please use z3c.ptcompat instead.

Usage
-----

When writing new code or modifying existing code, import page template
classes from the ``z3c.ptcompat`` package:

  >>> from z3c.ptcompat import PageTemplateFile
  >>> from z3c.ptcompat import ViewPageTemplateFile

Two methods are available to bind templates and template macros to a
view:

   >>> from z3c.ptcompat import bind_template
   >>> from z3c.ptcompat import bind_macro

Both function return render-methods that accept keyword arguments
which will be passed to the template.
   
   >>> render = bind_template(template, view)
   >>> render = bind_macro(template, view, request, macro)

Patches
-------

By loading the ``patches`` module, Zope view page template classes
will be monkey-patched to use the ``z3c.pt`` rendering facilities:

  <include package="z3c.ptcompat.patches" />

This is an alternative to changing module import locations.
