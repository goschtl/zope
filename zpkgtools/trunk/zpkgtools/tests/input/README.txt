=======================
Test Input for **zpkg**
=======================

This directory contains a bunch of sample input trees to use with zpkg
and the tests.  This is not a package itself, though it contains
(top-level) packages (as well as non-package directories).  The sample
resources are quite minimal; they don't represent *useful* resources.

Making this directory not be a package itself allows zpkg to actually
be able to package itself without losing test data.
