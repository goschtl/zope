import sys
import os
import traceback
import textwrap
import atexit
import shutil
import tempfile
import unzip
from StringIO import StringIO

import zLOG

from utils import EggProduct
from utils import EggProductContext
from App.config import getConfiguration

import pkg_resources

entrypoint_group = 'zope2.initialize'

class Basket(object):
    def __init__(self):
        self.pre_initialized = False
        self.exploded_dirs = []
        atexit.register(self.cleanup)
        self.usingTempDirs = False
        try:
            etc = os.path.join(INSTANCE_HOME, 'etc')
        except NameError: # INSTANCE_HOME may not be available?
            etc = ''
            self.usingTempDirs = True
        self.pdist_fname = os.path.join(etc, 'PRODUCT_DISTRIBUTIONS.txt')
        
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

        debug_mode = getConfiguration().debug_mode

        if not self.pre_initialized: # this services unit testing
            self.preinitialize()

        data = []
        points = pkg_resources.iter_entry_points(entrypoint_group)
        meta_types = []

        for point in points:
            # XXX deal with duplicate product names by raising an exception
            # somewhere in here.
            eggtitle = ' '.join(textwrap.wrap(point.dist.location, 80))
            try:
                product_pkg = get_containing_package(point.module_name)
            except:
                zLOG.LOG('Egg Product Init', zLOG.ERROR,
                         'Problem initializing product with entry point '
                         '"%s" in module "%s"' % (point.name,
                                                  point.module_name),
                         error=sys.exc_info())
                if debug_mode:
                    raise
                else:
                    continue
                
            productname = product_pkg.__name__.split('.')[-1]
            initializer = get_initializer(point, productname, product_pkg,
                                          debug_mode)
            context = EggProductContext(productname, initializer, app,
                                        product_pkg, eggtitle)
            returned = context.install(debug_mode)
            data.append(returned)

        return data

    def product_distributions_by_dwim(self):
        """ Return all product distributions which have an appropriate
        entry point group on sys.path """
        environment = pkg_resources.Environment()
        product_distros = []
        for project_name in environment:
            distributions = environment[project_name]
            for distribution in distributions:
                if is_product_distribution(distribution):
                    product_distros.append(distribution)
        return product_distros

    def product_distributions_by_require(self):
        """ Return all product distributions which are listed in the
        product distributions file """
        pdist_file = open(self.pdist_fname, 'r')
        strings = self.parse_product_distributions_file(pdist_file)
        product_distros = []
        for string in strings:
            distribution = pkg_resources.get_distribution(string)
            if is_product_distribution(distribution):
                product_distros.append(distribution)
            else:
                zLOG.LOG('Egg Product Init',
                         zLOG.ERROR,
                         'A requirement was listed in %s that is not a Zope '
                         'product package: %s' % (self.pdist_fname, string))
        return product_distros

    def ensureExplodedDir(self, project_name):
        if self.usingTempDirs:
            return tempfile.mkdtemp('', 'Basket_')
        
        var = os.path.join(INSTANCE_HOME, 'var')
        if not os.path.isdir(var):
            raise IOError, "With a instance home, a '%s' directory must exist" % var
            
        cacheDir = os.path.join(var, 'Basket', 'cache')
        if not os.path.isdir(cacheDir):
            os.makedirs(cacheDir)
        
        distDir = os.path.join(cacheDir, project_name)
        if not os.path.isdir(distDir):
            os.mkdir(distDir)

        return distDir
        

    def preinitialize(self):
        by_require = self.pdist_fname and os.path.exists(self.pdist_fname)
        if by_require:
            distributions = self.product_distributions_by_require()
        else:
            distributions = self.product_distributions_by_dwim()

        working_set = pkg_resources.working_set

        for distribution in distributions:
            if is_zip_safe_distribution(distribution):
                working_set.add(distribution)
            else:
                if os.path.isdir(distribution.location):
                    # already a directory
                    working_set.add(distribution)
                    continue
                # if it's not zip-safe and not already a directory, blast
                # it out to a dir and create new distro out of the
                # file-based egg
                if by_require: # these get added to the working set in req mode
                    remove_distribution_from_working_set(distribution)
                explodedDir = self.ensureExplodedDir(distribution.project_name)
                self.exploded_dirs.append(explodedDir)
                eggname = os.path.basename(distribution.location)
                eggdir = os.path.join(explodedDir, eggname)
                
                if not os.path.isdir(eggdir):
                    os.makedirs(eggdir)
                
                timestamp = os.path.join(explodedDir, 'timestamp-%s' % eggname)
                if not os.path.isfile(timestamp) or \
                        os.path.getmtime(distribution.location) > os.path.getmtime(timestamp):
                    
                    un = unzip.unzip()
                    un.extract(distribution.location, eggdir)
                    f = open(timestamp, 'w')
                    f.close()
                    atime = os.path.getatime(distribution.location)
                    mtime = os.path.getmtime(distribution.location)
                    os.utime(timestamp, (atime, mtime))

                metadata = pkg_resources.PathMetadata(eggdir,
                                        os.path.join(eggdir, 'EGG-INFO'))
                new_distro = pkg_resources.Distribution.from_filename(
                    eggdir, metadata=metadata)
                working_set.add(new_distro)

        self.pre_initialized = True

    def cleanup(self, emptyCacheDir=False):
        if self.usingTempDirs or emptyCacheDir:
            for explodedDir in self.exploded_dirs:
                shutil.rmtree(explodedDir, ignore_errors=True)
            

def get_containing_package(module_name):
    __import__(module_name)
    thing = sys.modules[module_name]
    if hasattr(thing, '__path__'):
        return thing
    new = '.'.join(module_name.split('.')[:-1])
    if new == module_name:
        return None
    return get_containing_package(new)

def get_initializer(point, productname, product_pkg, debug_mode):
    initializer = None
    try:
        # this will raise an import error if the initializer can't
        # be imported (presumably because of a module-scope error)
        initializer = point.load()
    except:
        zLOG.LOG('Zope', zLOG.ERROR, 'Could not import %s' % productname,
                 error = sys.exc_info())
        f = StringIO()
        limit = 100 # limit to 100 stack trace entries
        traceback.print_exc(limit, f)
        product_pkg.__import_error__ = f.getvalue()
        if debug_mode:
            raise
    return initializer

def is_product_distribution(distribution): 
    entry_meta = 'entry_points.txt'
    if distribution.has_metadata(entry_meta):
        inifile = distribution.get_metadata(entry_meta)
        sections = pkg_resources.split_sections(inifile)
        for section, content in sections:
            if section == entrypoint_group:
                return True

def is_zip_safe_distribution(distribution):
    return not distribution.has_metadata('not-zip-safe')

def remove_distribution_from_working_set(distribution):
    # XXX this is nasty... there maybe should be a pkg_resources API for this
    # or perhaps it's just never supposed to be done
    working_set = pkg_resources.working_set
    working_set.entries.remove(distribution.location)
    del working_set.by_key[distribution.key]
    working_set.entry_keys[distribution.location] = []
    sys.path.remove(distribution.location)
