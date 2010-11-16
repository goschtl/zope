====================
SequenceTable Widget
====================

This package provides a Sequence Widget just as
zope.app.form.browser.sequencewidget.
The main difference is that it places the subobject's fields horizontally in
a table. That means a kind of voucher-item forms are piece of cake to do.

There is also a widget (SequenceTableJSWidget) which does the add/remove item
in the browser with javascript.
The trick is to embed an invisible template of an empty row in the HTML,
add that each time a new row is required.

Drawbacks of JS:
 * Validation is done ONLY when the complete form is submitted to the server.
 * Submitting the form and using the Back button of the browser does not work.

WARNING!
========
The subobject MUST have subwidgets. That is usually the case if the subobject
is based on zope.schema.Object.

TODO
====
Tests.
Some are there, some are copied from z.a.form.browser and need fix.