zope.pytest
****************************

Introduction
============

This package contains a set of helper functions to test zope/grok using pytest

Core functions
==============

zope.pytest.setup.create_app

 * this function creates a wsgi app object which utilize a temporary db.

zope.pytest.setup.configure

 * this function parses zcml file and initialize the component registry

zope.pytest.setup.argument

 * this is a function decorator which register a function as an argument for 
   pytest functions


Simple example::

    from zope.pytest import create_app, configure, argument
    from my.project import Root

    @argument
    def app(request):
        return create_app(request, Root())

    @argument
    def config(request):
        return configure(request, my.project, 'ftesting.zcml')

    def test_hello(app, config):
        pass


Interact
=========
