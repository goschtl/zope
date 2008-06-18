"""Access to product-specific configuration.

"""
__docformat__ = "reStructuredText"

import zope.testing.cleanup

_configs = {}

zope.testing.cleanup.addCleanUp(_configs.clear)


def getProductConfiguration(name):
    """Return the product configuration for product `name`.

    If there is no configuration for `name`, None is returned.

    """
    return _configs.get(name)


def setProductConfigurations(configs):
    """Initialize product configuration from ZConfig data."""
    pconfigs = {}
    for pconfig in configs:
        pconfigs[pconfig.getSectionName()] = pconfig.mapping
    _configs.clear()
    _configs.update(pconfigs)


class FauxConfiguration(object):
    """Configuration object that can be use from tests.

    An instance is of this is similar to a <product-config> section from a
    zope.conf file in all the ways this module cares about.

    """

    def __init__(self, name, mapping):
        self.name = name
        self.mapping = dict(mapping)

    def getSectionName(self):
        return self.name
