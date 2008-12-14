hurry.js.wforms
***************

Introduction
============

This library packages wforms_ for `hurry.resource`_. 

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource

.. _wforms: http://www.formassembly.com/wForms/

How to use?
===========

You can import ``wforms`` like this::

  from hurry.js.wforms import wforms

And then to trigger inclusion in the web page, anywhere within
your page or widget rendering code, do this::

  wforms.need()

This requires integration between your web framework and
``hurry.resource``, and making sure that the original resources
(shipped in the ``resources`` directory in ``hurry.js.wforms``) are
published to some URL.

The package has already been integrated for Grok_ and Zope 3. If you
depend on the `hurry.zoperesource`_ package along with
``hurry.js.wforms`` in your ``setup.py``, the above example should work
out of the box.

.. _`hurry.zoperesource`: http://pypi.python.org/pypi/hurry.zoperesource

.. _Grok: http://grok.zope.org

Preparing hurry.js.wforms before release
========================================

This section is only relevant to release managers of ``hurry.js.wforms``; if 
you don't know whether you are, you aren't.

When releasing ``hurry.js.wforms``, an extra step should be
taken. Follow the regular package `release instructions`_, but before
egg generation (``python setup.py register sdist upload``) first
execute ``bin/wformsprepare <version number>`` (you may have to run
``buildout`` first to install the prepare command), where version
number is the version of the wforms release, such as ``1.0``. This will
download the code of that version and place it in the egg. After that
you can upload it.

.. _`release instructions`: http://grok.zope.org/documentation/how-to/releasing-software
