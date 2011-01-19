
import pytt 
import pytest

from pytt.app import Example
from zope.pytest import create_app, configure


def pytest_funcarg__app(request):
    return create_app(request, Example())

def pytest_funcarg__config(request):
    return configure(request, pytt, 'ftesting.zcml')

