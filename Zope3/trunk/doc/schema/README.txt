=========================
Zope Schema Documentation
=========================

This directory contains documentation on how to use schemas in Zope.
The documents are in reStructuredText format; you can read them as
plain text or you can convert them to other formats using docutils 0.3
or newer.

Converting to HTML
------------------

The docutils package includes a collection of conversion scripts in
the tools/ directory of the distribution.  You can use the html.py
script to convert to HTML for viewing in a browser; I recommend the
following set of options::

   python .../docutils-0.3/tools/html.py --pep-references \
       --rfc-references --link-stylesheet file.txt > file.html

You'll need to copy the stylesheet from the docutils distribution for
a better presentation::

    cp .../docutils-0.3/tools/stylesheets/default.css .

Tweak the stylesheet to suit your tastes; removing the entry for the
CSS selector "tt" (which sets a background color for an inline text
element) certainly makes the result more readable for documents that
contain a lot of references to programming language constructs.
