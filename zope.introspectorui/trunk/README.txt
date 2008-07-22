zope.introspectorui
*******************

What is zope.introspectorui?
==========================

`zope.introspectorui` is a set of views for the information objects provided
by zope.introspector.

Installing zope.introspectorui
==============================

`zope.introspectorui` is provided as an Python egg on cheeseshop and set
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

Because `zope.introspectorui` is a developer tool, you normally use it
by including the package the `setup.py` file of your own
package. There will most probably a section called `install_requires`
where you add 'zope.introspector' like this::

      ...
      install_requires=['setuptools',
                        # Add extra requirements here
                        'zope.introspectorui',
                        ...
                        ],

In `zc.buildout` based package setups you can 'activate' usage of
`zope.introspectorui` afterwards simply by (re)running `bin/buildout`.

