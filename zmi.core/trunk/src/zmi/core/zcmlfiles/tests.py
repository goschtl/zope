import unittest
from zope.testing.doctestunit import DocTestSuite

def test_include():
    """
    >>> from zope.configuration import xmlconfig, config
    >>> context = config.ConfigurationMachine()
    >>> xmlconfig.registerCommonDirectives(context)
    >>> import zmi.core.zcmlfiles

    >>> import warnings
    >>> showwarning = warnings.showwarning
    >>> warnings.showwarning = lambda *a, **k: None

    >>> xmlconfig.include(context, package=zmi.core.zcmlfiles)

    >>> xmlconfig.include(context, 'configure.zcml', zmi.core.zcmlfiles)
    >>> xmlconfig.include(context, 'ftesting.zcml', zmi.core.zcmlfiles)
    >>> xmlconfig.include(context, 'menus.zcml', zmi.core.zcmlfiles)
    >>> xmlconfig.include(context, 'meta.zcml', zmi.core.zcmlfiles)
    >>> xmlconfig.include(context,
    ...     'file_not_exists.zcml', zmi.core.zcmlfiles) #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    IOError: ...

    >>> warnings.showwarning = showwarning
    """

def test_suite():
    return unittest.TestSuite((
        DocTestSuite(),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
