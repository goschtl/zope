=================
hurry.jquerytools
=================

Introduction
============

This library packages jquerytools_ for `hurry.resource`_. It relies on
hurry.jquery for the dependency.

.. _jquerytools: http://flowplayer.org/tools/index.html 
.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource

Please take note that for now only the minified version of jquerytools is used.
This is because i don't found a proper download location for the different
versions of download.

How to use?
===========

You can import Slimbox from ``hurry.jquerytools`` and ``.need`` it where you want
these resources to be included on a page::

  from hurry.jquerytools import jquerytools

  .. in your page or widget rendering code, somewhere ..

  jquerytools.need()

This requires integration between your web framework and ``hurry.resource``,
and making sure that the original resources are published to some URL.

The package has already been integrated for Grok_ and Zope 3. If you depend
on the `hurry.zoperesource`_ package in your ``setup.py``, the above example
should work out of the box. Make sure to depend on the `hurry.zoperesource`_
package in your ``setup.py``.

.. _`hurry.zoperesource`: http://pypi.python.org/pypi/hurry.zoperesource

.. _Grok: http://grok.zope.org

Preparing hurry.jquerytools before release
==========================================

This section is only relevant to release managers of ``hurry.jquerytools``.

When releasing ``hurry.jquerytools``, an extra step should be taken. Follow the
regular package `release instructions`_, but before egg generation (``python
setup.py register sdist upload``) first execute ``bin/jquerytoolsprepare``. This
will download the jquerytools library and place it in the egg. (The version number
is currently hardcoded in the hurry.jquerytools.prepare module).

.. _`release instructions`: http://grok.zope.org/documentation/how-to/releasing-software
