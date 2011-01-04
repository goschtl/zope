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

def test_integration(config, app):
    view = component.getMultiAdapter(
        (Example(), request), name=u"index")
    assert "Congratulations" in view()
