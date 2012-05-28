import mypkg2
from zope.component import queryUtility
from mypkg2.interfaces import IFoo
from zope.pytest import configure

def pytest_funcarg__config_ftesting(request):
    # register components in 'ftesting.zcml'
    return configure(request, mypkg2, 'ftesting.zcml')

def pytest_funcarg__config_ftesting2(request):
    # register components in 'ftesting2.zcml'
    return configure(request, mypkg2, 'ftesting2.zcml')


def test_get_utility(config_ftesting):
    # we can get a utility registered in 'ftesting.zcml'
    util = queryUtility(IFoo, name='foo utility', default=None)
    assert util is not None

def test_dofoo_utility(config_ftesting):
    util = queryUtility(IFoo, name='foo utility', default=None)
    assert util().do_foo() == 'Foo!'


# The following tests are 'numbered', so we can be sure they are run
# in this very order. They should prove proper test separation
# regarding ZCML registrations.
def test_zcml_separation0(config_ftesting):
    # the utilites from ftesting.zcml are available in this test (and
    # the ones from ftesting2.zcml are not)
    util1 = queryUtility(IFoo, name='baz', default=None)
    util2 = queryUtility(IFoo, name='foo utility', default=None)
    assert util1 is None
    assert util2 is not None

def test_zcml_separation1(config_ftesting2):
    # the utilites from ftesting2.zcml are available in this test (and
    # the ones from ftesting.zcml are not, although they were
    # registered in the previous test.
    util1 = queryUtility(IFoo, name='baz', default=None)
    util2 = queryUtility(IFoo, name='foo utility', default=None)
    assert util1 is not None
    assert util2 is None
