About zope.products
===================

This package is a container for add-on packages for the Zope
Application (zope.app).  They are a part of the Zope project, but not
part of core Zope. These add-on products:

  - Are in some sense "standard".  They may provide widely-used
    components (e.g. common content types) or they might provide
    examples used to document or teach.

  - Do not require special software.  Anybody who can install Zope can
    run these packages without any additional software. This excludes
    most database interfaces, for example.

  - Will be refactored when Zope is refactored.

    This means that these products must have adequate unit and/or
    functional tests. These tests must be understandable, so that
    people doing refactoring have a prayer of getting failing tests
    running without pulling their hare out.

  - Will have identified contacts who are willing to help out by at
    least answering questions when issues arise during refactoring.
    They should include a MAINTAINER.txt file identifying that
    contact.

  - May be removed if they become too dificult to maintain or are
    hudged not to be worth the effort.

  - May or may not be included in Zope distributions.


Example packages
----------------

Example applications or packages should be placed in the
zope.products.demo package. The same above rules apply.
