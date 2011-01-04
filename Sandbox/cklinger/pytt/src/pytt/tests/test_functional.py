# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import pytt 
import pytest

from zope import component
from pytt.app import Example
from zope.publisher.browser import TestRequest
from zope.pytest import create_app, configure, argument

from infrae.testbrowser.browser import Browser


request = TestRequest()

@argument
def app(request):
    return create_app(request, Example())

@argument
def config(request):
    return configure(request, pytt, 'ftesting.zcml')

def test_with_infrae_testbrowser(config, app):
    browser = Browser(app)
    browser.options.handle_errors = False
    browser.open('http://localhost/test')
    assert browser.status == '200 Ok' 
