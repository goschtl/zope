Introduction
************

:mod:`zope.pytest` contains a set of helper functions to test
Zope_/Grok_ using pytest_.

Use pytest_ for your Zope_/Grok_ tests
======================================

Many Zope_/Grok_ applications today are tested using regular Python
:mod:`unittest` and/or the respective zope packages, testrunners, etc.

Many Python developers, however, prefer the more pythonic way of
pytest_ to detect, execute and evaluate tests.

:mod:`zope.pytest` now brings the power and beauty of pytest_ into
Zope_/Grok_ projects.

Quickstart
**********

Zope_ applications normally have to setup a ZODB_ database and
configure the Zope_ component architecture to run. At least
integration and functional tests therefore have to perform a lot of
setup/teardown functionality. That's where :mod:`zope.pytest` comes to
rescue.

With :mod:`zope.pytest` you can define `pytest`_-compatible
setup/teardown code simply like this::

    import mypkg
    from mypkg.app import MyApp
    from zope.pytest import configure, create_app

    def pytest_funcarg__config(request):
        return configure(request, mypkg, 'ftesting.zcml')

    def pytest_funcarg__app(request):
        return create_app(request, MyApp())

    def test_app(config, app):
        assert 1 is 1

This setup requires that you provide a valid configuration in an
``ftesting.zcml`` file in your package.

.. _project_setup:

Activating pytest_ and :mod:`zope.pytest` in your project
*********************************************************

In the ``buildout.cfg`` of your project simply add ``pytest`` as a
requirement to build tests. This can for instance be done like this::

    [buildout]
    develop = . 
    parts = test
    versions = versions

    [versions]

    [test]
    recipe = zc.recipe.egg
    eggs = 
        mypkg [tests]
        pytest

The ``test`` extra requirement mentioned in the ``[test]`` section can
be setup like this in your project's ``setup.py``::

    tests_require = [
        'pytest',
        'zope.app.appsetup',
        'zope.pytest',
        ]

    setuptools.setup(
        # ...
          extras_require = {
          'tests': tests_require,
          # ...
        }
    )

That's it. Run `buildout` and a `py.test` script should be created in
your ``bin/`` directory. Now you can go on and write your tests.


.. _pytest: http://pytest.org/
.. _Zope: http://www.zope.org/
.. _Grok: http://grok.zope.org/
.. _ZODB: http://www.zodb.org/
