======
README
======

This package provides an error reporting utility which is able to store errors.
Let's create one:

  >>> from zope.app.error.error import ErrorReportingUtility
  >>> util = ErrorReportingUtility()
  >>> util
  <zope.app.error.error.ErrorReportingUtility object at ...>
  
  >>> from zope.app.error.interfaces import IErrorReportingUtility
  >>> IErrorReportingUtility.providedBy(util)
  True
