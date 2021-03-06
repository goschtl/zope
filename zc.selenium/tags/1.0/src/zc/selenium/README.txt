===========================
Selenium testing for Zope 3
===========================

This package provides an easy way to use Selenium tests for Zope 3
applications.  It provides Selenium itself as a resource directory,
and it provides a test suite listing generated from registered views,
allowing different packages to provide tests without a central list of
tests to be maintained.

Selenium test views can also be written in Python using the
`zc.selenium.pytest` module.  This can make tests substantially easier
to write.


Selenium Issues
---------------

There is a known issue in the included version of Selenium; this
affects clicking on images in MSIE.  The Selenium bug report for this
problem is here:

    http://jira.openqa.org/browse/SRC-99

A patch in the file is provided in the file:

    Selenium-Core-SRC-99.patch

It is not known whether this patch should always be applied.
