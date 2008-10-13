hurry.tinymce
*************

Introduction
============

This library packages TinyMCE_ for `hurry.resource`_. 

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource

.. _TinyMCE: http://tinymce.moxiecode.com/

How to use?
===========

You can import ``tinymce`` like this::

  from hurry.tinymce import tinymce

And then to trigger inclusion in the web page, anywhere within
your page or widget rendering code, do this::

  tinymce.need()

This requires integration between your web framework and
``hurry.resource``, and making sure that the original resources
(shipped in the ``tinymce-build`` directory in ``hurry.tinymce``) are
published to some URL.

The package has already been integrated for Grok_ and Zope 3. If you
depend on the `hurry.zopetinymce`_ package in your ``setup.py``, the
above example should work out of the box.

.. _`hurry.zopetinymce`: http://pypi.python.org/pypi/hurry.zopetinymce

.. _Grok: http://grok.zope.org

Preparing hurry.tinymce before release
======================================

This section is only relevant to release managers of ``hurry.tinymce``; if 
you don't know whether you are, you aren't.

When releasing ``hurry.tinymce``, an extra step should be
taken. Follow the regular package `release instructions`_, but before
egg generation (``python setup.py register sdist upload``) first
execute ``bin/tinymceprepare <version number>``, where version number is
the version of the TinyMCE release, such as ``3.2.0.2``. This will download
the TinyMCE code of that version and place it in the egg.

.. _`release instructions`: http://grok.zope.org/documentation/how-to/releasing-software

