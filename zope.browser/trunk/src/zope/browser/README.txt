======
README
======

This package provides shared browser components for Zope 3.


ITerms
------

The ITerms interface is used as a base for ISource widget implementations. This
interfaces get used by zope.app.form and was initially defined in
zope.app.form.browser.interfaces.py. This makes it impossible to use for other
packages like z3c.form wihtout to depend on zope.app.form. Moving such base
components or interfaces to zope.browser will make it possible to share such
base components.

There is not much we can test except that ITerms is importable and an interface:

  >>> import zope.interface
  >>> from zope.browser import interfaces
  >>> zope.interface.Interface.providedBy(interfaces.ITerms)
  True
