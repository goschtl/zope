import unittest
import os
import sys
import copy
import Products
from Products.Basket.utils import EggProductContext
from Products.Basket import get_containing_package
import pkg_resources
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
import OFS
from Interface import Interface
import App.config
import zLOG

here = os.path.dirname(__file__)

class LogInterceptor:

    _old_log_write = None
    logged = None

    def _catch_log_errors( self, ignored_level=zLOG.PROBLEM ):

        if self._old_log_write is not None:
            return

        def log_write(subsystem, severity, summary, detail, error):
            if severity > ignored_level:
                assert 0, "%s(%s): %s" % (subsystem, severity, summary)
            if self.logged is None:
                self.logged = []
            self.logged.append( ( subsystem, severity, summary, detail ) )

        self._old_log_write = zLOG.log_write
        zLOG.log_write = log_write

    def _ignore_log_errors( self ):

        if self._old_log_write is None:
            return

        zLOG.log_write = self._old_log_write
        del self._old_log_write

class DummyProduct:
    def __init__(self, id):
        self.id = id

class DummyPackage:
    def __init__(self):
        # need to be in __dict__
        self.__name__ = 'Products.Basket.tests'
        self.__path__ = os.path.split(here)[:-1]

class DummyApp(ObjectManager):

    def __init__(self):
        self.Control_Panel = SimpleItem()
        self.Control_Panel.id = 'Control_Panel'
        self.Control_Panel.Products = ObjectManager()
        self.Control_Panel.Products.id = 'Products'
        
    def _manage_remove_product_meta_type(self, product):
         # hahahahahaha
         # hahahahahahahaahaha
         pass

class DummyProductContext:

    def __init__(self, product_name):
        self._ProductContext__app = DummyApp()
        self._ProductContext__prod = DummyProduct(product_name)
        self._ProductContext__pack = DummyPackage()

    def registerClass(self, *arg, **kw):
         self.arg = arg
         self.kw = kw

class IDummyRegisterableClass(Interface):
    pass

class DummyRegisterableClass:
    icon = 'p_/foo'
    meta_type = 'Dummy Registerable Class'
    __implements__ = IDummyRegisterableClass

def dummy_initializer(context):
    return 'initializer called'

def legacymethod(self):
    pass

class TestBasket(unittest.TestCase, LogInterceptor):

    def setUp(self):
        self.working_set = pkg_resources.working_set
        self.oldsyspath = sys.path[:]
        self.oldsysmodules = copy.copy(sys.modules)
        self.oldentries = self.working_set.entries[:]
        self.oldby_key = copy.copy(self.working_set.by_key)
        self.oldentry_keys = copy.copy(self.working_set.entry_keys)
        self.old_callbacks = self.working_set.callbacks[:]
        self.oldproductpath = Products.__path__
        self.fixtures = os.path.join(here, 'fixtures')
        self.old_debug_mode = App.config.getConfiguration().debug_mode
        self.logged = []

    def tearDown(self):
        sys.path[:] = self.oldsyspath
        sys.modules.clear()
        sys.modules.update(self.oldsysmodules)
        working_set = self.working_set
        working_set.entries[:] = self.oldentries
        working_set.by_key.clear()
        working_set.by_key.update(self.oldby_key)
        working_set.entry_keys.clear()
        working_set.entry_keys.update(self.oldentry_keys)
        working_set.callbacks[:] = self.old_callbacks
        Products.__path__[:] = self.oldproductpath
        App.config.getConfiguration().debug_mode = self.old_debug_mode

    def _getTargetClass(self):
        from Products.Basket import Basket
        return Basket

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_pkg_resources_monkeypatch(self):
        self.assertEqual(sys.modules['pkg_resources'],
                         pkg_resources)

    def test_require_success(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        self.failIf(sys.modules.has_key('Products.product1'))
        self.failIf(sys.modules.has_key('Products.product2'))

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='product1>=0.1')
        basket.require(distro_str='product2>=0.1')

        import Products.product1
        import Products.product2

        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))

    def test_require_fail(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        self.assertRaises(pkg_resources.DistributionNotFound,
                          basket.require,
                          distro_str='product1>=0.2')

    def test_initialize(self):
        basket = self._makeOne()
        basket.pre_initialized = True
        
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='product1>=0.1')
        basket.require(distro_str='product2>=0.1')
                
        result = basket.initialize(DummyProductContext('Basket'))
        self.assertEqual(result, ['product1 initialized',
                                  'product2 initialized'])
        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))

    def test_initialize_of_broken_at_import_in_debug_mode(self):
        basket = self._makeOne()
        basket.pre_initialized = True
        App.config.getConfiguration().debug_mode = True
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='brokenatimport>=0.1')
                
        self.assertRaises(ImportError, basket.initialize,
                          DummyProductContext('Basket'))

    def test_initialize_of_broken_at_import_no_debug_mode(self):
        basket = self._makeOne()
        basket.pre_initialized = True
        App.config.getConfiguration().debug_mode = False
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='brokenatimport>=0.1')
                
        self._catch_log_errors(zLOG.ERROR)
        try:
            basket.initialize(DummyProductContext('Basket'))
        finally:
            self._ignore_log_errors()

        self.assertEqual(len(self.logged), 1)
        warning = self.logged[0]
        self.assertEqual(warning[1], zLOG.ERROR)
        self.failUnless(warning[2].startswith('Problem initializing'))

    def test_initialize_of_broken_at_initialize_debug_mode(self):
        basket = self._makeOne()
        basket.pre_initialized = True
        App.config.getConfiguration().debug_mode = True
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='brokenatinitialize>=0.1')
                
        self.assertRaises(ValueError, basket.initialize,
                          DummyProductContext('Basket'))

    def test_initialize_of_broken_at_initialize_no_debug_mode(self):
        basket = self._makeOne()
        basket.pre_initialized = True
        App.config.getConfiguration().debug_mode = False
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='brokenatinitialize>=0.1')
        self._catch_log_errors(zLOG.ERROR)
        try:
            basket.initialize(DummyProductContext('Basket'))
        finally:
            self._ignore_log_errors()
        self.assertEqual(len(self.logged), 1)
        warning = self.logged[0]
        self.assertEqual(warning[1], zLOG.ERROR)
        self.failUnless(warning[2].startswith('Couldn\'t install'))

    def test_parse_product_distributions_file(self):
        from StringIO import StringIO
        fp = StringIO("jammyjam>0.1\n\njohnnyjoe>=0.2\n\n")
        basket = self._makeOne()
        basket.pre_initialized = True
        distributions = basket.parse_product_distributions_file(fp)
        expected = ['jammyjam>0.1', 'johnnyjoe>=0.2']
        self.assertEqual(distributions, expected)

    def test_source_egg(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        basket.require(distro_str='diskproduct1')
        result = basket.initialize(DummyProductContext('Basket'))
        self.assertEqual(result, ['diskproduct1 initialized'])

    def test_product_distributions_by_dwim(self):
        basket = self._makeOne()
        basket.pre_initialized = True

        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        distributions = basket.product_distributions_by_dwim()
        expected = [ 'diskproduct1', 'product1', 'product2' ]
        # don't consider other eggs that happen to be on the path, only
        # test that we find the things that are in our fixture dir
        actual = [ dist.key for dist in distributions if dist.key in expected ]
        self.assertEqual(sorted(expected), sorted(actual))

    def test_preinitalize_pdist_file_success(self):
        basket = self._makeOne()
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        pdist = os.path.join(self.fixtures, 'pdist-ok.txt')
        self.assertEqual(basket.pre_initialized, False)
        basket.preinitialize(pdist)
        self.assertEqual(basket.pre_initialized, True)

        import Products.product1
        import Products.product2
        self.assertRaises(ImportError,
                          self._importProduct,
                          'Products.diskproduct1')
        
        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))
        self.failIf(sys.modules.has_key('Products.diskproduct1'))
        
    def test_preinitalize_pdist_file_fail(self):
        basket = self._makeOne()
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        pdist = os.path.join(self.fixtures, 'pdist-fail.txt')
        self.assertEqual(basket.pre_initialized, False)
        self.assertRaises(pkg_resources.DistributionNotFound,
                          basket.preinitialize,
                          pdist)
        self.assertEqual(basket.pre_initialized, False)

        self.failIf(sys.modules.has_key('Products.product1'))
        self.failIf(sys.modules.has_key('Products.product2'))
        self.failIf(sys.modules.has_key('Products.product3'))
        self.failIf(sys.modules.has_key('Products.diskproduct1'))

        import Products.product1
        import Products.product2
        self.assertRaises(ImportError,
                          self._importProduct,
                          'Products.product3')
        self.assertRaises(ImportError,
                          self._importProduct,
                          'Products.diskproduct1')
        
        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))
        self.failIf(sys.modules.has_key('Products.product3'))
        self.failIf(sys.modules.has_key('Products.diskproduct1'))

    def test_preinitialize_missing_pdist(self):
        basket = self._makeOne()
        sys.path.append(self.fixtures)
        self.working_set.add_entry(self.fixtures)

        pdist = os.path.join(self.fixtures, 'nothere.txt')
        # falls back to dwim mode

        self.assertEqual(basket.pre_initialized, False)
        basket.preinitialize(pdist)
        self.assertEqual(basket.pre_initialized, True)

        import Products.product1
        import Products.product2
        import Products.diskproduct1

        self.failUnless(sys.modules.has_key('Products.product1'))
        self.failUnless(sys.modules.has_key('Products.product2'))
        self.failUnless(sys.modules.has_key('Products.diskproduct1'))

    def test_get_containing_package(self):
        self.assertEqual(
            get_containing_package('Products.PageTemplates.PageTemplate'
                                   ).__name__,
            'Products.PageTemplates')
        self.assertEqual(
            get_containing_package('Shared.DC.ZRDB').__name__,
            'Shared.DC.ZRDB')

    def _importProduct(self, name):
        __import__(name)

class TestEggProductContext(unittest.TestCase):

    def tearDown(self):
        if sys.modules.has_key('Dummy.Foo'):
            del sys.modules['Dummy.Foo']
        if sys.modules.has_key('Dummy.Bar'):
            del sys.modules['Dummy.Bar']
        import Products
        L = []
        if hasattr(Products, 'meta_types'):
            for thing in Products.meta_types:
                if not thing.has_key('test_chicken'):
                    L.append(thing)
            Products.meta_types = tuple(L)
        Products.__ac_permissions__ = ()
        from Globals import ApplicationDefaultPermissions as g
        for k, v in g.__dict__.items():
            if (k.startswith('_') and k.endswith('_Permission') and
                k.find('Dummy') > -1):
                delattr(g, k)
        from OFS.ObjectManager import ObjectManager as o
        for k, v in o.__dict__.items():
            if k.find('legacy') > -1:
                delattr(o, k)

    def _getTargetClass(self):
        from Products.Basket.utils import EggProductContext
        return EggProductContext

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_constructor(self):
        app = DummyApp()
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        data = context.install()
        self.assertEqual(data, 'initializer called')
        self.assertEqual(context.productname, 'DummyProduct')
        self.assertEqual(context.initializer, dummy_initializer)
        self.assertEqual(context.package, package)
        self.assertEqual(context.product.__class__.__name__, 'EggProduct')

    def test_module_aliases_set(self):
        app = DummyApp()
        package = DummyPackage()
        package.__module_aliases__ = (
            ('Dummy.Foo', 'Products.Basket'),
            ('Dummy.Bar', 'Products.Basket')
            )
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        data = context.install()
        self.assertEqual(data, 'initializer called')
        self.assertEqual(sys.modules['Dummy.Foo'].__name__,
                         'Products.Basket')
        self.assertEqual(sys.modules['Dummy.Bar'].__name__,
                         'Products.Basket')

    def test_misc_under_set(self):
        app = DummyApp()
        package = DummyPackage()
        def afunction():
            pass
        package.misc_ = {'afunction':afunction}
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        data = context.install()
        from OFS import Application
        self.assertEqual(
            Application.misc_.misc_.__dict__['DummyProduct']['afunction'],
            afunction)

    def test__ac_permissions__set(self):
        app = DummyApp()
        package = DummyPackage()
        package.__ac_permissions__ = ( ('aPermission', (), () ), )
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        data = context.install()
        from OFS.Folder import Folder
        self.assert_( ('aPermission', (),)  in Folder.__ac_permissions__)

    def test_module_meta_types_munged(self):
        app = DummyApp()
        package = DummyPackage()
        package.meta_types = ( {'name':'grabass', 'action':'amethod'}, )
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        data = context.install()
        from OFS.Folder import Folder
        self.assertEqual(({'action': 'amethod', 'product': 'DummyProduct',
                          'name': 'grabass', 'visibility': 'Global'},),
                         package.meta_types)

    def test_methods_set(self):
        app = DummyApp()
        package = DummyPackage()
        package.methods = {'amethod':dummy_initializer}
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        data = context.install()
        from OFS.Folder import Folder
        self.assertEqual(Folder.amethod.im_func, dummy_initializer)

    def test_create_product_object(self):
        import Globals
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        product = products.DummyProduct
        self.assertEqual(product.__class__.__name__, 'EggProduct')
        self.assertEqual(product.id, 'DummyProduct')
        self.assertEqual(product.title,
            'Installed egg product DummyProduct (0.1-this-is-a-test-fixture) '
                         'from eggname')
        self.assertEqual(product.version, '0.1-this-is-a-test-fixture')
        self.assertEqual(product.icon, 'misc_/Basket/icon_egg.gif')
        self.failUnless(product.home.find('Basket') > -1)
        self.assertEqual(product.manage_options[:-1],
                (Folder.manage_options[0],) + tuple(Folder.manage_options[2:]))
        self.assertEqual(product._distribution, None)
        self.assertEqual(product.manage_distribution, None)
        self.assertEqual(product.thisIsAnInstalledProduct, 1)
        self.assertEqual(product.manage_options[-1],
                         {'label':'README', 'action':'manage_readme'})
        self.assertEqual(Globals.__disk_product_installed__, 1)
        self.assertEqual(product.name, 'DummyProduct')

    def test_create_product_object_twice_returns_same(self):
        from Acquisition import aq_base
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        product = products.DummyProduct
        ob = context.create_product_object()
        self.assertEqual(id(aq_base(product)), id(aq_base(ob)))

    def test_product_with_error_recreation(self):
        import Globals
        from Acquisition import aq_base
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        product = products.DummyProduct
        package.__import_error__ = 'yup'
        del Globals.__disk_product_installed__
        ob = context.create_product_object()
        self.failIfEqual(id(aq_base(product)), id(aq_base(ob)))
        self.assertEqual(ob.manage_options[0],
                         {'label':'Traceback', 'action':'manage_traceback'})

    def test_registerClass_commonargs(self):
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        def constructor(self, id):
            pass
        def constructor2(self, id):
            pass
        def container_filter(foo):
            pass
        constructors = (constructor, constructor2)
        context.registerClass(DummyRegisterableClass,
                              constructors = constructors,
                              container_filter=container_filter)
        from Globals import ApplicationDefaultPermissions as g
        self.assertEqual(
            g._Add_Dummy_Registerable_Classs_Permission, ('Manager',))

        # hahahahahaha <loud bang>
        misc = dict(package._m.__dict__['ob'].__dict__)
        self.assertEqual(misc['constructor'], constructor)
        self.assertEqual(misc['constructor__roles__'], context.pr)
        self.assertEqual(misc['constructor2'], constructor2)
        self.assertEqual(misc['constructor2__roles__'], context.pr)
        
        found = False
        import Products
        for product in Products.meta_types:
            if product['product'] == 'DummyProduct':
                found = True
                eq = self.assertEqual
                eq(product['name'], 'Dummy Registerable Class')
                eq(product['permission'], 'Add Dummy Registerable Classs')
                eq(product['interfaces'][0], IDummyRegisterableClass)
                eq(product['visibility'], 'Global')
                eq(product['action'],
                   'manage_addProduct/DummyProduct/constructor')
                eq(product['container_filter'], container_filter)
        if not found:
            raise AssertionError, 'Dummy Product not found'

    def test_registerClass_legacy_aliased(self):
        from OFS.ObjectManager import ObjectManager
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        legacy = [('legacymethod2', legacymethod)]
        def constructor(self):
            pass
        context.registerClass(DummyRegisterableClass,
                              constructors = (constructor,),
                              legacy = legacy)
        self.assertEqual(ObjectManager.legacymethod.im_func, legacymethod)
        self.assertEqual(ObjectManager.legacymethod2.im_func, legacymethod)
        self.assertEqual(ObjectManager.legacymethod__roles__, context.pr)
        self.assertEqual(ObjectManager.legacymethod2__roles__, context.pr)

    def test_registerClass_constructor_tuples(self):
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        def constructor(self, id):
            pass
        def constructor2(self, id):
            pass
        constructors = (('constructora', constructor),
                        ('constructorb',constructor2))
        context.registerClass(DummyRegisterableClass,
                              constructors = constructors)
        misc = dict(package._m.__dict__['ob'].__dict__)
        self.assertEqual(misc['constructora'], constructor)
        self.assertEqual(misc['constructora__roles__'], context.pr)
        self.assertEqual(misc['constructorb'], constructor2)
        self.assertEqual(misc['constructorb__roles__'], context.pr)

    def test_registerClass_with_permission(self):
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        def constructor(self, id):
            pass
        constructors = (constructor,)
        context.registerClass(DummyRegisterableClass,
                              permission = 'Appease This Stupid Machinery',
                              constructors = constructors)
        from Globals import ApplicationDefaultPermissions as g
        self.assertEqual(
            g._Appease_This_Stupid_Machinery_Permission, ('Manager',))

    def test_registerClass_with_interfaces(self):
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        def constructor(self, id):
            pass
        constructors = (constructor,)
        class IFooInterface(Interface):
            pass
        context.registerClass(DummyRegisterableClass,
                              constructors = constructors,
                              interfaces = (IFooInterface,))

        found = False
        import Products
        for product in Products.meta_types:
            if product['product'] == 'DummyProduct':
                found = True
                self.assertEqual(product['interfaces'][0], IFooInterface)
        if not found:
            raise AssertionError, 'Dummy Product not found'

    def test_registerClass_with_icon(self):
        app = DummyApp()
        products = app.Control_Panel.Products
        package = DummyPackage()
        context = self._makeOne('DummyProduct', dummy_initializer, app, package,
                                'eggname')
        def constructor(self, id):
            pass
        context.registerClass(DummyRegisterableClass,
                              constructors = (constructor,),
                              icon = 'fixtures/new.gif')
        misc = getattr(OFS.misc_.misc_, 'DummyProduct')
        self.assertEqual(misc['new.gif'].__class__.__name__, 'ImageResource')

class TestEggProduct(unittest.TestCase):
    def _getTargetClass(self):
        from Products.Basket.utils import EggProduct
        return EggProduct

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_manage_get_product_readme__(self):
        product = self._makeOne('foo', 'foo product', 'Products.Basket.tests')
        self.assertEqual(product.manage_get_product_readme__().strip(),
                         'This is a test fixture, beeyotch!')


class TestResource(unittest.TestCase):

    def test_is_zipped(self):
        from Products.Basket.resource import is_zipped
        self.failUnless(is_zipped('Products.product1'))
        self.failUnless(is_zipped('Products.product2'))
        self.failIf(is_zipped('Products.diskproduct1'))
        self.failIf(is_zipped('Products.Basket'))

    def test_page_template_resource(
        self, path='www/test_zpt.zpt',  module='Products.product1'):
        from Products.PageTemplates import PageTemplateResource
        zpt = PageTemplateResource(path, module=module)
        self.assertEqual(zpt.__name__, os.path.basename(path))
        expected = pkg_resources.resource_string(module, path)
        self.assertEqual(zpt.read(), expected)

    def test_disk_page_template_resource(self):
        self.test_page_template_resource(module='Products.diskproduct1')

    def test_cant_import_resources_from_basket(self):
        for cls in ('PageTemplateResource', 'DTMLResource', 'ImageResource'):
            try:
                exec 'from Products.Basket.resource import %s' % cls
            except ImportError:
                pass
            else:
                self.fail(
                    'Should not be able to import %s from Basket.resource')

    def test_dtml_resource(
        self, path='www/test_dtml', module='Products.product1'):
        from Globals import DTMLResource
        dtml = DTMLResource(path, module=module)
        self.assertEqual(dtml.__name__, os.path.basename(path))
        expected = pkg_resources.resource_string(module, path + '.dtml')
        self.assertEqual(dtml.read_raw(), expected)

    def test_disk_dtml_resource(self):
        self.test_dtml_resource(module='Products.diskproduct1')

    def test_image_resource(
        self, path='www/test_image.jpg', module='Products.product1'):
        from Globals import ImageResource
        img = ImageResource(path, module=module)
        self.assertEqual(img.content_type, 'image/jpeg')
        expected = pkg_resources.resource_string(module, path)
        self.assertEqual(img.read(), expected)

    def test_disk_image_resource(self):
        self.test_image_resource(module='Products.diskproduct1')


def sorted(L):
    L.sort()
    return L

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBasket))
    suite.addTest(makeSuite(TestEggProductContext))
    suite.addTest(makeSuite(TestResource))
    suite.addTest(makeSuite(TestEggProduct))
    return suite

