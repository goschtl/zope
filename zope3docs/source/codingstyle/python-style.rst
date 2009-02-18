Writing Python code
===================

Use PEP 8
---------

In general any Python code should be written accordingly to PEP 8.

.. note::
    Please be aware that PEP 8 recommends module-level consistency over blind
    rule-following. Zope 3 has been around for a while and earlier coding style of
    modules might not match thec current rules. In that case, please make a
    conscious decision about a reasonable level of consistency.

Additional rules
----------------

Attribute names
~~~~~~~~~~~~~~~

The naming of attributes as recommended by PEP 8 is controversial. PEP 8
prefers `attribute_name` over `attributeName`. Zope 3 has been built originally
with the latter rule and many APIs still use this meme. 

Newer packages usually prefer to use underscores instead of camel case.

Import ordering
~~~~~~~~~~~~~~~

XXX Jim recommended ordering imports not as PEP 8 does (by creating blocks) 
but by simply using the output of `sort` on the block.

This rule has not been officially agreed upon.


Catch specific errors, keep try blocks minimal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are converting a value to an `int`, and you want to catch conversion
errors, you need only catch `ValueError`. Be sure to do the minimum possible
between your `try:` and `except ValueError:` statements.


No trailing whitespace
~~~~~~~~~~~~~~~~~~~~~~

Trailing whitespace should not occur, nor should blank lines at the end of
files.
