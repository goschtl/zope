hurry.yui
*********

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
example should work out of the box.

.. _`hurry.zopeyui`: http://pypi.python.org/pypi/hurry.zopeyui

.. _Grok: http://grok.zope.org

Preparing hurry.yui before release
==================================

This section is only relevant to release managers of ``hurry.yui``; if 
you don't know whether you are, you aren't.

When releasing ``hurry.yui``, an extra step should be taken. Follow
the regular package `release instructions`_, but before egg generation
(``python setup.py register sdist upload``) first execute
``bin/yuiprepare <version number>``, where version number is the
version of the YUI release, such as ``2.6.0``. This will do two
things:

* download the YUI of that version and place it in the egg

* download the YUI dependency structure of that YUI version and generate
  a ``yui.py`` file in the package that reflects this.

.. _`release instructions`: http://grok.zope.org/documentation/how-to/releasing-software
