import mypkg
from zope.component import queryUtility
from mypkg.app import IFoo
from zope.pytest import configure

def pytest_funcarg__config(request):
    return configure(request, mypkg, 'ftesting.zcml')

def test_get_utility(config):
    util = queryUtility(IFoo, name='foo utility', default=None)
    assert util is not None

def test_dofoo_utility(config):
    util = queryUtility(IFoo, name='foo utility', default=None)
    assert util().do_foo() == 'Foo!'
