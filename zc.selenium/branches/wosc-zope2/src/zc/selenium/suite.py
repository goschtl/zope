import zc.selenium.pytest


class Suite(object):
    """docstring"""

    def suite(self):
        return zc.selenium.pytest.suite(self.request)
