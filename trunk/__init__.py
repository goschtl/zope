import sys
import os
import pkg_resources
import traceback

from Products.Basket.utils import EggProductContext
from Products.Basket.utils import EggProduct
import zLOG
import App

entrypoint_group = 'zope2.initialize'

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
        context.registerClass(EggProduct, constructors = (('dummy',None),),
                              visibility=None, icon='icon_egg.gif')
        # Grab app from Zope product context
        # It's a "protected" attribute, hence the name mangling
        app = context._ProductContext__app
        debug_mode = App.config.getConfiguration().debug_mode

        if not self.pre_initialized:
            try:
                home = INSTANCE_HOME
                etc = os.path.join(home, 'etc')
            except NameError: # INSTANCE_HOME may not be available
                etc = ''
            pdist_fname = os.path.join(etc, 'PRODUCT_DISTRIBUTIONS.txt')
            self.preinitialize(pdist_fname)

        data = []
        points = pkg_resources.iter_entry_points(entrypoint_group)
        meta_types = []

        for point in points:
            # XXX deal with duplicate product names by raising an exception
            # somewhere in here.
            try:
                product_pkg = get_containing_package(point.module_name)
            except:
                if debug_mode:
                    raise
                else:
                    zLOG.LOG('Egg Product Init', zLOG.ERROR,
                             'Problem initializing product with entry point '
                             '%s in module %s' % (point.name,point.module_name),
                             error=sys.exc_info())
                    continue
                
            productname = product_pkg.__name__.split('.')[-1]
            initializer = get_initializer(point, productname, debug_mode)
            context = EggProductContext(productname, initializer, app,
                                        product_pkg)
            # XXX debug mode conditions raise_exc, log_exc
            returned = context.install(debug_mode)
            data.append(returned)
        return data

    def product_distributions_by_dwim(self):
        """ Find all product distributions which have an appropriate
        entry point group on sys.path """
        environment = pkg_resources.Environment()
        ns_meta = 'entry_points.txt'
        product_distros = []
        for project_name in environment:
            distributions = environment[project_name]
            for distribution in distributions:
                if distribution.has_metadata(ns_meta):
                    inifile = distribution.get_metadata(ns_meta)
                    sections = pkg_resources.split_sections(inifile)
                    for section, content in sections:
                        if section == entrypoint_group:
                            product_distros.append(distribution)
                            break
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

def get_containing_package(module_name):
    __import__(module_name)
    thing = sys.modules[module_name]
    if hasattr(thing, '__path__'):
        return thing
    new = '.'.join(module_name.split('.')[:-1])
    if new == module_name:
        return None
    return get_containing_package(new)

def get_initializer(point, productname, debug_mode):
    initializer = None
    try:
        # this will raise an import error if the initializer can't
        # be imported (presumably because of a module-scope error)
        initializer = point.load()
    except:
        exc = sys.exc_info()
        zLOG.LOG('Zope', zLOG.ERROR, 'Could not import %s' % productname,
                 error=exc)
        f = StringIO()
        traceback.print_exc(100, f)
        product_pkg.__import_error__ = f.getvalue()
        if debug_mode:
            raise exc[0], exc[1], exc[2]
    return initializer

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

# Poke the resource classes into the Zope package tree where they will 
# wind up in a future zope version, maybe
import resource

import Globals
Globals.ImageResource = resource.ImageResource
Globals.DTMLResource = resource.DTMLResource

from Products import PageTemplates
PageTemplates.PageTemplateResource = resource.PageTemplateResource

# Prevent anyone from importing from here
del resource.ImageResource
del resource.DTMLResource
del resource.PageTemplateResource

