hurry.extjs
***********

Introduction
============

This library packages ExtJS_ for `hurry.resource`_.

.. _`hurry.resource`: http://pypi.python.org/pypi/hurry.resource

.. _ExtJS: http://www.extjs.com/

How to use?
===========

In order to avoid licenses conflicts, first you need to download ExtJS_ and place it in your
project. Once it's finished, add `hurry.zoperesource` and `hurry.extjs` to your setup.py
and run ./bin/buildout::

        install_requires=[
           ...,
           'hurry.zoperesource'
           'hurry.extjs',
        ],

Next step, it's to publish the sources of ExtJS as a resource directory. Using Grok,
you should have something like this in your configure.zcml::

    <configure xmlns="http://namespaces.zope.org/zope"
               xmlns:grok="http://namespaces.zope.org/grok"
               xmlns:browser="http://namespaces.zope.org/browser">

      <include package="grok" />
      <includeDependencies package="." />
      <grok:grok package="." />

      <include package="hurry.zoperesource" />

      <browser:resourceDirectory
          name="extjs"
          directory="ext-2.2.1" />

    </configure>

`hurry.extjs` will look for the resourceDirectory named `extjs`, so it's important that
you use the same name in the resourceDirectory statement.

Now, you can import ``extjs`` like this::

  from hurry.extjs import extjs_all, extjs_css

And then to trigger inclusion in the web page, anywhere within
your page or widget rendering code, do this::

  extjs_all.need()
  extjs_css.need()


Authors
-------

- Santiago Videla
