Overview
========

A diff tool that bridges zope.schema with difflib.

It allows you to take two objects and retrieve a field-by-field diff;
fields are chosen based on all implemented interfaces, unless
explicitly specified.

A browser view is included to easily display a diff between two
objects using difflib's ``HtmlDiff``-class.
