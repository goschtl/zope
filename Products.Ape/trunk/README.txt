
Quick Start
===========

Assuming you already have Zope set up and working, follow these steps
to get started with Ape.

1. Check your Zope version.  These instructions require Zope 2.7.

2. Add the Ape product to Zope by placing it in the Products
directory.  If you're using an INSTANCE_HOME setup, place it with your
other add-on products.

3. Open component.xml, provided by the Ape product, in a text editor.
Copy one of the sample configurations to your zope.conf, changing it
to fit your system.

4. Start Zope.

5. If you mounted the database somewhere other than the root, visit
the Zope management interface.  Select "ZODB Mount Point" from the
"add" drop-down.  Click the "Create selected mount points" button.

6. Visit the portion of the object database stored using Ape and add
things to it.  As you add objects, they will appear on the filesystem
or in your database.


Tutorial
========

A tutorial on the Ape library was prepared and delivered at PyCon
2003.  The text of the tutorial, called 'outline.txt', is in the 'doc'
subdirectory.  The accompanying slides, in OpenOffice Impress format,
are somewhat out of date, but can be downloaded at the following URL:

http://cvs.zope.org/Products/Ape/doc/tutorial_slides.sxi?rev=HEAD&content-type=application/octet-stream


Adding New Object Types
=======================

After reading the tutorial, see doc/apexml.txt for instructions on how
to make Ape aware of other object types.  Although Ape can store any
kind of ZODB object, Ape stores a Python pickle when no specific
mapper is provided for a class.  Use apeconf.xml files to configure
new mappers.
