zope.pytest
***********

Introduction
============

This package contains a set of helper functions to test Zope/Grok
using `pytest`_. It currently lacks special support for doctesting.


Core functions
==============

`zope.pytest.setup.create_app`

 * this function creates a WSGI app object which utilizes a temporary db.

`zope.pytest.setup.configure`

 * this function parses ZCML files and initializes the component registry


Simple example::

    import my.project
    from zope.pytest import create_app, configure
    from my.project import Root

    def pytest_funcarg__app(request):
        return create_app(request, Root())

    def pytest_funcarg__config(request):
        return configure(request, my.project, 'ftesting.zcml')

    def test_hello(app, config):
        assert 1 == 1

Documentation
=============

Complete documentation can be found on

http://packages.python.org/zope.pytest

.. _pytest: http://pytest.org/
