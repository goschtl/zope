import pytest
from zope.pytest import configure, create_app
from mypkg4.app import SampleApp

def pytest_funcarg__apps(request):
    app = SampleApp()
    return app, create_app(request, app)

def pytest_funcarg__config(request):
    return configure(request, mypkg4, 'ftesting.zcml')

def pytest_runtest_setup(item):
    pytest.set_trace()

