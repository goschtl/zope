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
