import sys
import os
import pkg_resources
import inspect
from utils import install_egg_product

class Basket(object):
    def __init__(self):
        self.pre_initialized = False
        
    def require(self, distro_str):
        """ Specifically require a distribution specification """
        pkg_resources.require(distro_str)

    def parse_product_distributions_file(self, fp):
        L = []
        for distro_str in fp:
            distro_str = distro_str.strip()
            if distro_str:
                L.append(distro_str)
        return L

    def initialize(self, context):
        if not self.pre_initialized:
            try:
                home = INSTANCE_HOME
                etc = os.path.join(home, 'etc')
            except NameError: # INSTANCE_HOME may not be available
                etc = ''
            pdist_fname = os.path.join(etc, 'PRODUCT_DISTRIBUTIONS.txt')
            self.preinitialize(pdist_fname)
        data = []
        points = pkg_resources.iter_entry_points('zope2.initialize')
        meta_types = []
        for point in points:
            initialize = point.load()
            context = EggProductContext(product, app, package)
            initialize(context)
        return data

    def product_distributions_by_dwim(self):
        environment = pkg_resources.Environment()
        ns_meta = 'namespace_packages.txt'
        product_distros = []
        for project_name in environment:
            distributions = environment[project_name]
            for distribution in distributions:
                if distribution.has_metadata(ns_meta):
                    packages = distribution.get_metadata(ns_meta)
                    lines = packages.splitlines()
                    if 'Products' in lines:
                        product_distros.append(distribution)
        return product_distros

    def preinitialize(self, pdist_fname=None):
        if pdist_fname and os.path.exists(pdist_fname):
            # do the explicit only-include-named-distributions behavior
            pdist_file = open(pdist_fname, 'r')
            strings = self.parse_product_distributions_file(pdist_file)
            for string in strings:
                self.require(string) # this calls 'add' for the distribution
        else:
            # do the implicit look-up-all-products-on-my-path behavior
            distributions = self.product_distributions_by_dwim()
            for distribution in distributions:
                pkg_resources.working_set.add(distribution)
        self.pre_initialized = True

basket = Basket()
initialize = basket.initialize

class Jackboot(object):
    """
    Nazi-like proxy for an object to replace this package in
    sys.modules... Basket is born deprecated, and nothing but the
    Zope core should try to use it... if you can get around this,
    you DESERVE TO LOSE! ;-)
    """
    def __setattr__(self, k, v):
        raise DeprecationWarning('This package is deprecated, '
                                 'do not monkey-patch it!')
    def __getattribute__(self, k):
        raise DeprecationWarning('This package is deprecated, do not import '
                                 'it directly!')



