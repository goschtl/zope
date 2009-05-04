hurry.extjs
***********

Introduction
============

This library packages ExtJS_ for `hurry.resource`_.

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource

.. _ExtJS: http://www.extjs.com/

How to use?
===========

ExtJS_ is distributed under the terms of the GPL v3 :

- http://extjs.com/products/license.php

In order to avoid licenses conflicts, first you need to download ExtJS_ and place it in your
home directory. Once it's finished, add `hurry.extjs` to your setup.py and run ./bin/buildout::

        install_requires=[
           ...,
           'hurry.extjs==2.2.1',
        ],

`hurry.extjs` will try to extract and copy the sources of ExtJS to a known location.
Note that you `must` always download and include the same versions of ExtJS_ and `hurry.extjs`

Now, you can import ``extjs`` like this::

  from hurry.extjs import extjs_all, extjs_css

And then to trigger inclusion in the web page, anywhere within
your page or widget rendering code, do this::

  extjs_all.need()
  extjs_css.need()


Authors
-------

- Santiago Videla
