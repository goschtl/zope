hurry.yui
*********

.. Important::
   hurry.yui has been superseded by
   `js.yui <http://pypi.python.org/pypi/js.yui>`_ package.

Introduction
============

This library packages YUI_ for `hurry.resource`_. It is aware of YUI's
dependency structure and different modes (normal, minified and debug)
and resource rollups.

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource

.. _YUI: http://developer.yahoo.com/yui/

How to use?
===========

You can import various bits of YUI from ``hurry.yui`` and ``.need``
them where you want these resources to be included on a page::

  from hurry import yui

  .. in your page or widget rendering code, somewhere ..

  yui.datatable.need()

All the module names as listed here_ are available in the
``hurry.yui`` package. In addition rolled up modules are also
available (such as ``reset_fonts_grids``), but rollup inclusion will
be done automatically so these need not to be referred to
explicitly. See the `hurry.resource`_ documentation for more
information.

.. _here: http://developer.yahoo.com/yui/yuiloader/#modulenames

This requires integration between your web framework and
``hurry.resource``, and making sure that the original resources
(shipped in the ``yui-build`` directory in ``hurry.yui``) are
published to some URL.

The package has already been integrated for Grok_ and Zope 3. If you
depend on the `hurry.zopeyui`_ package in your ``setup.py``, the above
example should work out of the box. Starting with version 2.6.0.4 you
do not need `hurry.zopeyui`_ anymore. Instead it is sufficient to
depend on the `hurry.zoperesource`_ package in your ``setup.py``.

.. _`hurry.zopeyui`: http://pypi.python.org/pypi/hurry.zopeyui

.. _`hurry.zoperesource`: http://pypi.python.org/pypi/hurry.zoperesource

.. _Grok: http://grok.zope.org

Preparing hurry.yui before release
==================================

This section is only relevant to release managers of ``hurry.yui``.

The javascript code that this package relies on is not checked into
subversion to sidestep the copyright policy of svn.zope.org. Instead,
just before release to pypi, an entry point is triggered that
downloads the appropriate javascript code. To trigger this automated
behavior you should do the release using ``bin/fullrelease``, which
uses zest.releaser configured with the appropriate entry points.

To update to a newer version of YUI, adjust the constants in
``hurry/yui/prepare.py``.
