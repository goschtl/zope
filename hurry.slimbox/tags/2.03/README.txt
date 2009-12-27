=============
hurry.slimbox
=============

Introduction
============

This library packages Slimbox_ for `hurry.resource`_. It relies on
hurry.jquery for the dependency.

.. _Slimbox: http://www.digitalia.be/software/slimbox2
.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource


How to use?
===========

You can import Slimbox from ``hurry.slimbox`` and ``.need`` it where you want
these resources to be included on a page::

  from hurry.slimbox import slimbox

  .. in your page or widget rendering code, somewhere ..

  slimbox.need()

This requires integration between your web framework and ``hurry.resource``,
and making sure that the original resources are published to some URL.

The package has already been integrated for Grok_ and Zope 3. If you depend
on the `hurry.zoperesource`_ package in your ``setup.py``, the above example
should work out of the box. Make sure to depend on the `hurry.zoperesource`_
package in your ``setup.py``.

.. _`hurry.zoperesource`: http://pypi.python.org/pypi/hurry.zoperesource

.. _Grok: http://grok.zope.org

Preparing hurry.slimbox before release
======================================

This section is only relevant to release managers of ``hurry.slimbox``.

When releasing ``hurry.slimbox``, an extra step should be taken. Follow the
regular package `release instructions`_, but before egg generation (``python
setup.py register sdist upload``) first execute ``bin/slimboxprepare``. This
will download the Slimbox library and place it in the egg. (The version number
is currently hardcoded in the hurry.slimbox.prepare module).

.. _`release instructions`: http://grok.zope.org/documentation/how-to/releasing-software
