Overview
========

This package implements a compatibility-layer between the following
Zope Page Template engines:

 * z3c.pt
 * zope.pagetemplate

Usage
-----

Import page template classes directly from this package:

  >>> from z3c.pt.compat import PageTemplateFile
  >>> from z3c.pt.compat import ViewPageTemplateFile

If the environment-variable ``PREFER_Z3C_PT`` is set to a true value,
the ``z3c.pt`` engine will be used instead of ``zope.pagetemplate``.

Binding methods
---------------

Two methods are available to bind templates and template macros to a
view:

   >>> from z3c.pt.compat import bind_template
   >>> from z3c.pt.compat import bind_macro

Both function return render-methods that accept keyword arguments
which will be passed to the template.
   
   >>> render = bind_template(template, view)
   >>> render = bind_macro(template, view, request, macro)



   
