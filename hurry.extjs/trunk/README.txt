hurry.extjs
***********

Introduction
============

This library packages ExtJS_ for `hurry.resource`_.

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource

.. _ExtJS: http://www.extjs.com/

How to use?
===========

First download ExtJS_ and place it in your home directory.
Once it's finished, add `hurry.extjs` to your setup.py and run ./bin/buildout::

        install_requires=[
           ...,
           'hurry.extjs==2.2.1',
        ],

Note that you `must` use always the same versions of ExtJS and `hurry.extjs`

Now, you can import ``extjs`` like this::

  from hurry.extjs import extjs_all, extjs_css

And then to trigger inclusion in the web page, anywhere within
your page or widget rendering code, do this::

  extjs_all.need()
  extjs_css.need()
