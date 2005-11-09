import time
import pkg_resources
import os
import re
import sys

import Globals
from Globals import ImageFile
from Globals import DTMLFile
from Globals import package_home
from Globals import InitializeClass
from OFS.content_types import guess_content_type
from App.Common import rfc1123_date
from App.special_dtml import defaultBindings
from OFS.misc_ import Misc_
import OFS

from OFS.Application import pgetattr
from OFS.Application import get_folder_permissions
from OFS import Application
from App.ProductContext import ProductContext
from App.ProductContext import AttrDict
from App.Product import Product
from App.Product import ihasattr
from App.Product import doInstall
from App.FactoryDispatcher import FactoryDispatcher
from OFS.Folder import Folder
import transaction

from OFS.ObjectManager import ObjectManager
from AccessControl.Permission import registerPermissions
from AccessControl.PermissionRole import PermissionRole
from Interface.Implements import instancesOfObjectImplements
import Products
import ZClasses

import zLOG

_marker = ()

## from Products.PageTemplates.PageTemplateFile import PageTemplateFile
## from Products.PageTemplates.PageTemplateFile import XML_PREFIX_MAX_LENGTH
## from zLOG import LOG
## from zLOG import ERROR
## from Globals import DevelopmentMode

## class PageTemplateResource(PageTemplateFile):
##     def _cook_check(self):
##         if self._v_last_read and not DevelopmentMode:
##             return
##         print self.filename
##         __traceback_info__ = self.filename
##         try:
##             mtime = os.path.getmtime(self.filename)
##         except OSError:
##             mtime = 0
##         if self._v_program is not None and mtime == self._v_last_read:
##             return
##         f = open(self.filename, "rb")
##         try:
##             text = f.read(XML_PREFIX_MAX_LENGTH)
##         except:
##             f.close()
##             raise
##         t = sniff_type(text)
##         if t != "text/xml":
##             # For HTML, we really want the file read in text mode:
##             f.close()
##             f = open(self.filename)
##             text = ''
##         text += f.read()
##         f.close()
##         self.pt_edit(text, t)
##         self._cook()
##         if self._v_errors:
##             LOG('PageTemplateFile', ERROR, 'Error in template',
##                 '\n'.join(self._v_errors))
##             return
##         self._v_last_read = mtime
        
class ImageResource(ImageFile):
    def __init__(self,path,_prefix=None):
        name = _prefix['__name__']
        resource = pkg_resources.resource_stream(name, path)

        data = resource.read()
        content_type, enc=guess_content_type(path, data)
        if content_type:
            self.content_type=content_type
        else:
            self.content_type='image/%s' % path[path.rfind('.')+1:]
        self.__name__=path[path.rfind('/')+1:]
        self.lmt=time.time()
        self.lmh=rfc1123_date(self.lmt)

class DTMLResource(DTMLFile):
    def __init__(self,name,_prefix=None, **kw):
        #DTMLFile.__init__(self, name, _prefix, **kw)
        self.ZBindings_edit(defaultBindings)
        self._setFuncSignature()

        #ClassicHTMLFile.__init__(self, name, _prefix, **kw)
        packagename = _prefix['__name__']
        if not kw.has_key('__name__'):
            kw['__name__'] = os.path.split(name)[-1]

        #FileMixin.__init__(self, *args, **kw)
        filename = name + '.dtml'
        self.raw = (packagename, filename)
        self.initvars(None, kw)
        self.setName(kw['__name__'] or filename)

    def read_raw(self):
        if self.edited_source:
            data = self.edited_source
        elif not self.raw:
            data = ''
        elif pkg_resources.resource_exists(*self.raw):
            data = pkg_resources.resource_stream(*self.raw).read()
        return data
        
    def _cook_check(self):
        if Globals.DevelopmentMode:
            __traceback_info__=str(self.raw)
            mtime = time.time()
            if mtime != self._v_last_read:
                self.cook()
                self._v_last_read=mtime
        elif not hasattr(self,'_v_cooked'):
            try: changed = self.__changed__()
            except: changed=1
            self.cook()
            if not changed:
                self.__changed__(0)

class EggProduct(Product):
    def __init__(self, id, title, packagename):
        self.id = id
        self.title = title
        self.packagename = packagename

    def manage_get_product_readme__(self):
        for fname in ('README.txt', 'README.TXT', 'readme.txt'):
            if pkg_resources.resource_exists(self.packagename, fname):
                return pkg_resources.resource_string(self.packagename, fname)
        return ''

    def _readRefreshTxt(self, pid=None):
        # egg products cannot be refreshed
        return None

    def manage_performRefresh(self, REQUEST=None):
        """ """
        # egg products can't be refreshed
        return

InitializeClass(EggProduct)

class EggProductContext(object):
    def __init__(self, productname, initializer, app, package):
        self.productname = productname
        self.initializer = initializer
        self.app = app
        self.package = package
        self.product = self.create_product_object()
        self.permissions = {}
        self.new_permissions = {}
        self.meta_types = {}
        
    def create_product_object(self):
        # Create a persistent object in the ControlPanel.Products area
        # representing a product packaged as an egg and set it as self.product
        products = self.app.Control_Panel.Products
        fver = ''

        packagename = self.package.__name__
        productname = self.productname

        ie = getattr(self.package, '__import_error__', None)

        # Retrieve version number from any suitable version.txt
        for fname in ('version.txt', 'VERSION.txt', 'VERSION.TXT'):
            if pkg_resources.resource_exists(packagename, fname):
                fver = pkg_resources.resource_string(packagename, fname).strip()
                break

        old = None

        if ihasattr(products, productname):
            old = getattr(products, productname)
            if ihasattr(old, 'version') and old.version == fver:
                old_ie = getattr(old, 'import_error_', None)
                if old_ie == ie:
                    # Version hasn't changed. Don't reinitialize.
                    return old

        f = fver and (" (%s)" % fver)
        product = EggProduct(productname, 'Installed egg product %s%s' %
                             (productname, f), packagename)

        if old is not None:
            assert hasattr(self.app, '_manage_remove_product_meta_type')
            self.app._manage_remove_product_meta_type(product)
            products._delObject(productname)
            for id, v in old.objectItems():
                try:
                    product._setObject(id, v)
                except:
                    zLOG.LOG('EggProductContext Initialization', zLOG.INFO,
                             ('Error when cleaning old persistent data from '
                              'Control Panel for %s.%s' % (productname, id)),
                             error=sys.exc_info())

        products._setObject(productname, product)
        product.icon = 'p_/InstalledProduct_icon'
        product.version = fver
        product.home = str(self.package.__path__)

        product.manage_options = (Folder.manage_options[0],) + \
                             tuple(Folder.manage_options[2:])
        product._distribution = None
        product.manage_distribution = None
        product.thisIsAnInstalledProduct = 1

        if ie:
            product.import_error_ = ie
            product.title = 'Broken product %s' % productname
            product.icon = 'p_/BrokenProduct_icon'
            product.manage_options = (
                {'label':'Traceback', 'action':'manage_traceback'},
                )

        for fname in ('README.txt', 'README.TXT', 'readme.txt'):
            if pkg_resources.resource_exists(packagename, fname):
                product.manage_options = product.manage_options+(
                    {'label':'README', 'action':'manage_readme'},
                    )
                break

        if not doInstall():
            transaction.abort()
            return product

        # Give the ZClass fixup code in Application
        Globals.__disk_product_installed__ = 1
        product.name = productname
        return product
    
    def registerClass(self, instance_class=None, meta_type='',
                      permission=None, constructors=(),
                      icon=None, permissions=None, legacy=(),
                      visibility="Global", interfaces=_marker,
                      container_filter=None
        ):
        """Register a constructor

        Keyword arguments are used to provide meta data:

        instance_class -- The class of the object that will be created.

        meta_type -- The kind of object being created
           This appears in add lists.  If not specified, then the class
           meta_type will be used.

        permission -- The permission name for the constructors.
           If not specified, then a permission name based on the
           meta type will be used.

        constructors -- A list of constructor methods
          A method can be a callable object with a __name__
          attribute giving the name the method should have in the
          product, or the method may be a tuple consisting of a
          name and a callable object.  The method must be pickleable.

          The first method will be used as the initial method called
          when creating an object.

        icon -- The name of an image file in the package to
                be used for instances. Note that the class icon
                attribute will be set automagically if an icon is
                provided.

        permissions -- Additional permissions to be registered
           If not provided, then permissions defined in the
           class will be registered.

        legacy -- A list of legacy methods to be added to ObjectManager
                  for backward compatibility

        visibility -- "Global" if the object is globally visible, None else

        interfaces -- a list of the interfaces the object supports

        container_filter -- function that is called with an ObjectManager
           object as the only parameter, which should return a true object
           if the object is happy to be created in that container. The
           filter is called before showing ObjectManager's Add list,
           and before pasting (after object copy or cut), but not
           before calling an object's constructor.

        """
        app = self.app
        package = self.package
        product = self.product

        if icon and instance_class is not None:
            setattr(instance_class, 'icon', 'misc_/%s/%s' %
                    (product.id, os.path.split(icon)[1]))

        if permissions:
            self.register_additional_permissions(permissions)

        pr, permission = self.register_constructor_permission(
                                     permission, meta_type, instance_class)
        self.pr = pr # for unit tests

        if legacy:
            self.register_legacy(legacy, pr)

        fd = self.get_factory_dispatcher(package)

        if not hasattr(package, '_m'):
            package._m = AttrDict(fd)

        if interfaces is _marker:
            if instance_class is None:
                interfaces = ()
            else:
                interfaces = instancesOfObjectImplements(instance_class)

        cname = self.register_constructors(constructors, package._m, pr)

        self.register_product_meta_type(meta_type, instance_class,
                                        product.id, cname, permission,
                                        visibility, interfaces,
                                        container_filter)

        if icon:
            self.register_icon(icon, product.id, cname)

    def register_additional_permissions(self, permissions):
        if isinstance(permissions, basestring): # You goofed it!
            raise TypeError, ('Product context permissions should be a '
                'list of permissions not a string', permissions)
        for p in permissions:
            if isinstance(p, tuple):
                p, default= p
                registerPermissions(((p, (), default),))
            else:
                registerPermissions(((p, ()),))

    def register_constructor_permission(self, permission, meta_type,
                                        instance_class):
        if permission is None:
            permission = "Add %ss" % (meta_type or instance_class.meta_type)

        if isinstance(permission, tuple):
            permission, default = permission
        else:
            default = ('Manager',)

        pr = PermissionRole(permission,default)
        registerPermissions(((permission, (), default),))
        return pr, permission

    def register_legacy(self, legacy, pr):
        for method in legacy:
            if isinstance(method, tuple):
                name, method = method
                aliased = 1
            else:
                name = method.__name__
                aliased = 0
            if not ObjectManager.__dict__.has_key(name):
                setattr(ObjectManager, name, method)
                setattr(ObjectManager, name + '__roles__', pr)
                if aliased:
                    # Set the unaliased method name and its roles
                    # to avoid security holes.  XXX: All "legacy"
                    # methods need to be eliminated.
                    setattr(ObjectManager, method.__name__, method)
                    setattr(ObjectManager, method.__name__+'__roles__', pr)

    def register_product_meta_type(self, meta_type,instance_class, productname,
                                   cname, permission, visibility, interfaces,
                                   container_filter):
        if not hasattr(Products, 'meta_types'):
            Products.meta_types = ()
        Products.meta_types = Products.meta_types+(
            { 'name': meta_type or instance_class.meta_type,
              'action': ('manage_addProduct/%s/%s' % (productname, cname)),
              'product': productname,
              'permission': permission,
              'visibility': visibility,
              'interfaces': interfaces,
              'instance': instance_class,
              'container_filter': container_filter,
              'test_chicken': True, # to allow unit tests to clean up
              },)

    def register_icon(self, icon_path, productname, cname):
        name = os.path.basename(icon_path)
        icon = ImageResource(icon_path, self.package.__dict__)
        icon.__roles__ = None
        if not hasattr(OFS.misc_.misc_, productname):
            setattr(OFS.misc_.misc_, productname,
                    OFS.misc_.Misc_(productname, {}))
        getattr(OFS.misc_.misc_, productname)[name] = icon

    def register_constructors(self, constructors, misc, pr):
        cname = None
        for method in constructors:
            if isinstance(method, tuple):
                name, method = method
            else:
                name = os.path.split(method.__name__)[-1]
            if cname is None:
                cname = name
            if not self.product.__dict__.has_key(name):
                misc[name] = method
                misc[name+'__roles__'] = pr
        return cname

    def get_factory_dispatcher(self, package):
        fd = getattr(package, '__FactoryDispatcher__', None)
        if fd is None:
            class __FactoryDispatcher__(FactoryDispatcher):
                "Factory Dispatcher for a Specific Product"

            fd = package.__FactoryDispatcher__ = __FactoryDispatcher__
        return fd

    def registerBaseClass(self, base_class, meta_type=None):
        #
        #   Convenience method, now deprecated -- clients should
        #   call 'ZClasses.createZClassForBase()' themselves at
        #   module import time, passing 'globals()', so that the
        #   ZClass will be available immediately.
        #
        Z = ZClasses.createZClassForBase( base_class, self.package )
        return Z


    def set_package_module_aliases(self):
        product_pkg = self.package
        if hasattr(product_pkg, '__module_aliases__'):
            for k, v in product_pkg.__module_aliases__:
                if not sys.modules.has_key(k):
                    if isinstance(v, basestring) and sys.modules.has_key(v):
                        v = sys.modules[v]
                    sys.modules[k] = v

    def set_package_misc_attrs(self):
        # Install items into the misc_ namespace, used by products
        # and the framework itself to store common static resources
        # like icon images.
        misc_=pgetattr(self.package, 'misc_', {})
        if misc_:
            if isinstance(misc_, dict):
                misc_ = Misc_(self.productname, misc_)
            Application.misc_.__dict__[self.productname]=misc_

    def set_package_ac_permissions(self):
        # Support old-old-style product metadata. Older products may
        # define attributes to name their permissions, meta_types,
        # constructors, etc.
        folder_permissions = get_folder_permissions()
        for p in pgetattr(self.package, '__ac_permissions__', ()):
            permission, names, default = (tuple(p) + ('Manager',))[:3]
            if names:
                for name in names:
                    self.permissions[name] = permission
            elif not folder_permissions.has_key(permission):
                self.new_permissions[permission]=()

    def munge_package_meta_types(self):
        for meta_type in pgetattr(self.package, 'meta_types', ()):
            # Modern product initialization via a ProductContext
            # adds 'product' and 'permission' keys to the meta_type
            # mapping. We have to add these here for old products.
            pname = self.permissions.get(meta_type['action'], None)
            if pname is not None:
                meta_type['permission']=pname
            meta_type['product']=self.productname
            meta_type['visibility'] = 'Global'

    def set_package_methods(self):
        for name, method in pgetattr(self.package, 'methods', {}).items():
            if not hasattr(Folder, name):
                setattr(Folder, name, method)
                if name[-9:]!='__roles__': # not just setting roles
                    if (self.permissions.has_key(name) and
                        not self.folder_permissions.has_key(
                            self.permissions[name])):
                        permission = self.permissions[name]
                        if self.new_permissions.has_key(permission):
                            self.new_permissions[permission].append(name)
                        else:
                            self.new_permissions[permission]=[name]

    def install(self, raise_exc=1, log_exc=1):
        __traceback_info__ = self.productname

        package = self.package
        product = self.product
        productname = self.productname
        initializer = self.initializer
        permissions = self.permissions
        folder_permissions = get_folder_permissions()
        init_data = None

        try:
            self.set_package_module_aliases()
            self.set_package_misc_attrs()
            init_data = initializer(self)
            self.set_package_ac_permissions()
            self.munge_package_meta_types()
            self.set_package_methods()

            if self.new_permissions:
                new_permissions = self.new_permissions.items()
                for permission, names in new_permissions:
                    folder_permissions[permission]=names
                new_permissions.sort()
                Folder.__ac_permissions__=tuple(
                    list(Folder.__ac_permissions__)+new_permissions)

            if not doInstall():
                transaction().abort()
            else:
                transaction.get().note('Installed product '+productname)
                transaction.commit()

        except:
            if log_exc:
                LOG('Zope',ERROR,'Couldn\'t install %s' % productname,
                    error=sys.exc_info())
            transaction.abort()
            if raise_exc:
                raise

        return init_data

    def registerHelp(self, *arg, **kw):
        return # this is so not worth it

    def getProductHelp(self):
        """
        Returns the ProductHelp associated with the current Product.
        """
        return None

    def registerHelpTopic(self, id, topic):
        """
        Register a Help Topic for a product.
        """
        pass

    def registerHelpTitle(self, title):
        """
        Sets the title of the Product's Product Help
        """
        pass


def import_product(product_dir, productname, raise_exc=0, log_exc=1):
    path_join=os.path.join
    isdir=os.path.isdir
    exists=os.path.exists
    _st=type('')
    global_dict=globals()
    silly=('__doc__',)
    modules=sys.modules
    have_module=modules.has_key

    try:
        package_dir=path_join(product_dir, productname)
        if not isdir(package_dir): return
        if not exists(path_join(package_dir, '__init__.py')):
            if not exists(path_join(package_dir, '__init__.pyc')):
                if not exists(path_join(package_dir, '__init__.pyo')):
                    return

        pname="Products.%s" % productname
        try:
            product=__import__(pname, global_dict, global_dict, silly)
            if hasattr(product, '__module_aliases__'):
                for k, v in product.__module_aliases__:
                    if not have_module(k):
                        if type(v) is _st and have_module(v): v=modules[v]
                        modules[k]=v
        except:
            exc = sys.exc_info()
            if log_exc:
                LOG('Zope', ERROR, 'Could not import %s' % pname,
                    error=exc)
            f=StringIO()
            traceback.print_exc(100,f)
            f=f.getvalue()
            try: modules[pname].__import_error__=f
            except: pass
            if raise_exc:
                raise exc[0], exc[1], exc[2]
    finally:
        exc = None
