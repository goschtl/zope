# -*- coding: utf-8 -*-
# Copyright (c) 2007-2010 NovaReto GmbH
# cklinger@novareto.de 

import pytt 
import pytest

from zope import component
from pytt.app import Example
from zope.publisher.browser import TestRequest
from zope.pytest import create_app, configure


#def pytest_funcarg__app(request):
#    return create_app(request, Example())
#
#def pytest_funcarg__config(request):
#    return configure(request, pytt, 'ftesting.zcml')

zope_req = TestRequest()

def test_integration(app, config):
    view = component.getMultiAdapter(
        (Example(), zope_req), name=u"index")
    assert "Congratulations" in view()
