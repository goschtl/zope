=====================================================
Demo Applications for ``z3c.form`` and ``z3c.formui``
=====================================================

This package is a ``mars`` implementation which seeks to duplicate the original
z3c.formdemo demo applications.

The original README is README.z3c.txt.

`Grok`_ is a project which seeks to ....

``Martian`` grew from `Grok`_:

 Martian provides a framework that allows configuration to be expressed
 in declarative Python code. These declarations can often be deduced
 from the structure of the code itself. The idea is to make these
 declarations so minimal and easy to read that even extensive
 configuration does not overly burden the programmers working with the
 code. Configuration actions are executed during a separate phase
 ("grok time"), not at import time, which makes it easier to reason
 about and easier to test.

 The ``martian`` package is a spin-off from the `Grok`_ project, in the
 context of which this codebase was first developed. While Grok uses
 it, the code is completely independent of Grok.

The ``mars`` packages which are included here as develop eggs grew from
answering the duties of the zcml directives used to configure the original
``z3c.formdemo`` demos. These packages use both `Grok`_ and ``Martian``.
``Martian`` to register the ``Grokkers`` and `Grok`_ does the grokking.

To this point I have incoporated only ``message``, ``spreadsheet``,
``questionnaire``, ``widgets`` and ``wizard``.
