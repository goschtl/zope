===========
Widget Demo
===========

This package demonstrates how to use fields and widgets.

You can find the widgets samples also in the onlinehelp rubric: 
Samples/Widgets.

You also need the package zope.app.styleguide for to include the
Style Guide.

Description
-----------

We use IRead.. and IWrite interfaces in the sample for use a easy
registration in the ZCML. The readonly attributes samples declared in the 
IRead interfaces. The write samples are registred with a addform and editfrom.
Ther is also a schemadisplay view registred called 'View' where you can see
the readonly sample field.

The sample fields are named like the attribute of the fields. The field in the
sample objects have the same order like the attributes in the constructor.
