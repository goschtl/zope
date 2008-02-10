import unittest

from zope.testing import doctest
from zope.configuration.config import ConfigurationMachine

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS

globs = dict(config=ConfigurationMachine())

def test_suite():
    return doctest.DocFileSuite(
            'adapter.txt', globs=globs,
            optionflags=optionflags
            )
