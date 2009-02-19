import zc.selenium.pytest


class Suite(object):
    """docstring to make Zope2 happy"""

    def suite(self):
        return zc.selenium.pytest.suite(self.request)
