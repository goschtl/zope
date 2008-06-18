zope.introspector
*****************

What is zope.introspector?
==========================

`zope.introspector` helps developers to get information about objects
in their Zope/Python runtime environment.

It provides an easy to use API that enables developers to create
'object descriptors' for any object and is usable in almost every Zope
environment, namely Zope 2, Zope 3 and Plone. Although
`zope.introspector` is mainly tested with Python 2.4, also Python 2.5
installs should work.

`zope.introspector` is extensible. That means, that you can write your
own descriptors for certain types of objects or aspects
thereof. Please see the detailed documentation in
'src/zope/introspector' to learn more about that.

The package does not provide viewing components. Instead you can use
packages, that are built on top of `zope.introspector`. These provide
viewing components, that apply to more specific frameworks like Plone
or Grok.

Installing zope.introspector
============================

`zope.introspector` is provided as an Python egg on cheeseshop and set
up via `zc.buildout`_

.. _zc.buildout: http://cheeseshop.python.org/pypi/zc.buildout

You may have setuptools already installed for your system Python. In
that case, you may need to upgrade it first because buildout requires
a very recent version::

    $ sudo easy_install -U setuptools

If this command fails because easy_install is not available, there is
a good chance you do not have setuptools available for your system
Python. If so, there is no problem because setuptools will be
installed locally by buildout.

Because `zope.introspector` is a developer tool, you normally use it
by including the package the `setup.py` file of your own
package. There will most probably a section called `install_requires`
where you add 'zope.introspector' like this::

      ...
      install_requires=['setuptools',
                        # Add extra requirements here
                        'zope.introspector',
                        ...
                        ],

In `zc.buildout` based package setups you can 'activate' usage of
`zope.introspector` afterwards simply by (re)running `bin/buildout`.

