hurry.jqueryui
**************

Introduction
============

This library packages `jQuery UI`_ for `hurry.resource`_. It is aware
of jQuery UI's structure and different modes (normal, minified).

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource
.. _`jQuery UI`: http://jqueryui.com/

How to use?
===========

You can import jQuery UI from ``hurry.jqueryui`` and ``.need`` it
where you want these resources to be included on a page::

  from hurry.jqueryui import jqueryui

  .. in your page or widget rendering code, somewhere ..

  jqueryui.need()

You can also use JQuery UI themes:

  from hurry.jqueryui import smoothness

This requires integration between your web framework and
``hurry.resource``, and making sure that the original resources
(shipped in the ``jqueryui-build`` directory in ``hurry.jqueryui``)
are published to some URL.

The package has already been integrated for Grok_ and the Zope
Toolkit. If you depend on the `hurry.zoperesource`_ package in your
``setup.py``, the above example should work out of the box. Make sure
to depend on the `hurry.zoperesource`_ package in your ``setup.py``.

.. _`hurry.zoperesource`: http://pypi.python.org/pypi/hurry.zoperesource

.. _Grok: http://grok.zope.org

Preparing hurry.jqueryui before release
=======================================

This section is only relevant to release managers of ``hurry.jqueryui``.
The javascript code that this package relies on is not checked into subversion
to sidestep the copyright policy of svn.zope.org. Instead, just before
release to pypi, an entry point is triggered that downloads the appropriate
javascript code. To trigger this automated behavior you should do the
release using ``bin/fullrelease``, which uses zest.releaser configured
with the appropriate entry points.
