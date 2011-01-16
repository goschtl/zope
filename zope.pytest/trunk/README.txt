zope.pytest
***********

Introduction
============

This package contains a set of helper functions to test zope/grok using pytest

Core functions
==============

zope.pytest.setup.create_app

 * this function creates a wsgi app object which utilize a temporary db.

zope.pytest.setup.configure

 * this function parses zcml file and initialize the component registry


Simple example::

    from zope.pytest import create_app, configure
    from my.project import Root

    def pytest_funcarg__app(request):
        return create_app(request, Root())

    def pytest_funcarg__config(request):
        return configure(request, my.project, 'ftesting.zcml')

    def test_hello(app, config):
        pass

Documentation
=============

Complete documentation can be found on

http://packages.python.org/zope.pytest
