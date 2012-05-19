Changelog
=========

1.1.0 - unreleased
------------------

* Update various imports to zope.formlib and require at least Zope 2.13.

* Deal with forward compatibility with Zope 4.

* Avoid charset negotiation.

1.0.4 - 2011-02-06
------------------

* Fix test failures when running against 2.13.2+.

1.0.3 - 2010-06-13
------------------

* Explicitly load the zope.app.form.browser ZCML.

* Avoid deprecation warnings under Zope 2.13.

1.0.2 - 2009-12-30
------------------

* Deal with backwards compatibility for the menuItemDirective.

1.0.1 - 2009-12-29
------------------

* Added backwards compatibility support with Zope 2.12. The protectClass
  function has moved. Also include our own meta.zcml into the tests runs to
  get a higher coverage.

1.0 - 2009-12-26
----------------

* The code was extracted from the Zope2 distribution. This distribution
  contains the code from both the Products.Five formlib and form sub-packages.
