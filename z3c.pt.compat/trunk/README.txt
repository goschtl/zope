Overview
========

This package implements a compatibility-layer between the following
Zope Page Template engines:

 * z3c.pt
 * zope.pagetemplate

Usage
-----

Use the following import-clause:

  >>> from z3c.pt.compat import ViewPageTemplateFile

If the environment-variable ``PREFER_Z3C_PT`` is set to a true value,
the ``z3c.pt`` engine will be used instead of ``zope.pagetemplate``.
