############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
__doc__='''Application support

$Id: Application.py,v 1.200 2004/01/11 15:32:44 chrism Exp $'''
__version__='$Revision: 1.200 $'[11:-2]

import Globals,Folder,os,sys,App.Product, App.ProductRegistry, misc_
import time, traceback, os,  Products
from DateTime import DateTime
from AccessControl.User import UserFolder
from App.ApplicationManager import ApplicationManager
from webdav.NullResource import NullResource
from FindSupport import FindSupport
from urllib import quote
from StringIO import StringIO
from AccessControl.PermissionRole import PermissionRole
from App.ProductContext import ProductContext
from misc_ import Misc_
import ZDOM
from zLOG import LOG, ERROR, WARNING, INFO
from zExceptions import Redirect as RedirectException, Forbidden
from HelpSys.HelpSys import HelpSys
from Acquisition import aq_base
from App.Product import doInstall
from App.config import getConfiguration

class Application(Globals.ApplicationDefaultPermissions,
                  ZDOM.Root, Folder.Folder,
                  App.ProductRegistry.ProductRegistry, FindSupport):
    """Top-level system object"""
    title    ='Zope'
    #__roles__=['Manager', 'Anonymous']
    __defined_roles__=('Manager','Anonymous','Owner')
    web__form__method='GET'
    isTopLevelPrincipiaApplicationObject=1
    _isBeingUsedAsAMethod_=0

    # Create the help system object
    HelpSys=HelpSys('HelpSys')

    p_=misc_.p_
    misc_=misc_.misc_

    _reserved_names=('Control_Panel',
                     'browser_id_manager',
                     'temp_folder')

    # This class-default __allow_groups__ ensures that the
    # emergency user can still access the system if the top-level
    # UserFolder is deleted. This is necessary to allow people
    # to replace the top-level UserFolder object.

    __allow_groups__=UserFolder()

    # Set the universal default method to index_html
    _object_manager_browser_default_id = 'index_html'

    _initializer_registry = None

    def title_and_id(self): return self.title
    def title_or_id(self): return self.title

    def __init__(self):
        # Initialize users
        uf=UserFolder()
        self.__allow_groups__=uf
        self._setObject('acl_users', uf)

        # Initialize control panel
        cpl=ApplicationManager()
        cpl._init()
        self._setObject('Control_Panel', cpl)
        get_transaction().note("Created Zope Application")

    def id(self):
        try:    return self.REQUEST['SCRIPT_NAME'][1:]
        except: return self.title

    def __class_init__(self): Globals.default__class_init__(self)

    def PrincipiaRedirect(self,destination,URL1):
        """Utility function to allow user-controlled redirects"""
        if destination.find('//') >= 0:
            raise RedirectException, destination
        raise RedirectException, ("%s/%s" % (URL1, destination))
    Redirect=ZopeRedirect=PrincipiaRedirect

    def __bobo_traverse__(self, REQUEST, name=None):

        try: return getattr(self, name)
        except AttributeError: pass
        try: return self[name]
        except KeyError: pass
        method=REQUEST.get('REQUEST_METHOD', 'GET')
        if not method in ('GET', 'POST'):
            return NullResource(self, name, REQUEST).__of__(self)

        # Waaa. unrestrictedTraverse calls us with a fake REQUEST.
        # There is proabably a better fix for this.
        try: REQUEST.RESPONSE.notFoundError("%s\n%s" % (name, method))
        except AttributeError:
            raise KeyError, name

    def PrincipiaTime(self, *args):
        """Utility function to return current date/time"""
        return apply(DateTime, args)
    ZopeTime=PrincipiaTime

    ZopeAttributionButton__roles__=None
    def ZopeAttributionButton(self):
        """Returns an HTML fragment that displays the 'powered by zope'
        button along with a link to the Zope site."""
        return '<a href="http://www.zope.org/Credits" target="_top"><img ' \
               'src="%s/p_/ZopeButton" width="115" height="50" ' \
               'border="0" alt="Powered by Zope" /></a>' % self.REQUEST.BASE1


    def DELETE(self, REQUEST, RESPONSE):
        """Delete a resource object."""
        self.dav__init(REQUEST, RESPONSE)
        raise Forbidden, 'This resource cannot be deleted.'

    def MOVE(self, REQUEST, RESPONSE):
        """Move a resource to a new location."""
        self.dav__init(REQUEST, RESPONSE)
        raise Forbidden, 'This resource cannot be moved.'

    test_url___allow_groups__=None
    test_url=ZopeAttributionButton

    def absolute_url(self, relative=0):
        '''The absolute URL of the root object is BASE1 or "/".'''
        if relative: return ''
        try:
            # Take advantage of computed URL cache
            return self.REQUEST['BASE1']
        except (AttributeError, KeyError):
            return '/'

    def absolute_url_path(self):
        '''The absolute URL path of the root object is BASEPATH1 or "/".'''
        try:
            return self.REQUEST['BASEPATH1'] or '/'
        except (AttributeError, KeyError):
            return '/'

    def virtual_url_path(self):
        '''The virtual URL path of the root object is empty.'''
        return ''

    def getPhysicalPath(self):
        '''Returns a path that can be used to access this object again
        later, for example in a copy/paste operation.  Designed to
        be used with getPhysicalRoot().
        '''
        # We're at the base of the path.
        return ('',)

    def getPhysicalRoot(self): return self

    fixupZClassDependencies__roles__=()
    def fixupZClassDependencies(self, rebuild=0):
        # Note that callers should not catch exceptions from this method
        # to ensure that the transaction gets aborted if the registry
        # cannot be rebuilt for some reason. Returns true if any ZClasses
        # were registered as a result of the call or the registry was
        # rebuilt.
        jar=self._p_jar
        result=0

        if rebuild:
            from BTrees.OOBTree import OOBTree
            jar.root()['ZGlobals'] = OOBTree()
            result = 1

        zglobals =jar.root()['ZGlobals']
        reg_has_key=zglobals.has_key

        products=self.Control_Panel.Products
        for product in products.objectValues():
            items=list(product.objectItems())
            finished_dict={}
            finished = finished_dict.has_key
            while items:
                name, ob = items.pop()
                base=aq_base(ob)
                if finished(id(base)):
                    continue
                finished_dict[id(base)] = None
                try:
                    # Try to re-register ZClasses if they need it.
                    if hasattr(base,'_register') and hasattr(base,'_zclass_'):
                        class_id=getattr(base._zclass_, '__module__', None)
                        if class_id and not reg_has_key(class_id):
                            ob._register()
                            result=1
                            if not rebuild:
                                LOG('Zope', INFO,
                                    'Registered ZClass: %s' % ob.id
                                    )
                    # Include subobjects.
                    if hasattr(base, 'objectItems'):
                        m = list(ob.objectItems())
                        items.extend(m)
                    # Try to find ZClasses-in-ZClasses.
                    if hasattr(base, 'propertysheets'):
                        ps = ob.propertysheets
                        if (hasattr(ps, 'methods') and
                            hasattr(ps.methods, 'objectItems')):
                            m = list(ps.methods.objectItems())
                            items.extend(m)
                except:
                    LOG('Zope', WARNING,
                        'Broken objects exist in product %s.' % product.id,
                        error=sys.exc_info())

        return result

    checkGlobalRegistry__roles__=()
    def checkGlobalRegistry(self):
        """Check the global (zclass) registry for problems, which can
        be caused by things like disk-based products being deleted.
        Return true if a problem is found"""
        try:
            keys=list(self._p_jar.root()['ZGlobals'].keys())
        except:
            LOG('Zope', ERROR,
                'A problem was found when checking the global product '\
                'registry.  This is probably due to a Product being '\
                'uninstalled or renamed.  The traceback follows.',
                error=sys.exc_info())
            return 1
        return 0

    _setInitializerRegistry__roles__ = ()
    def _setInitializerFlag(self, flag):
        if self._initializer_registry is None:
            self._initializer_registry = {}
        self._initializer_registry[flag] = 1

    _getInitializerRegistry__roles__ = ()
    def _getInitializerFlag(self, flag):
        reg = self._initializer_registry
        if reg is None:
            reg = {}
        return reg.get(flag)

class Expired(Globals.Persistent):
    icon='p_/broken'

    def __setstate__(self, s={}):
        dict=self.__dict__
        if s.has_key('id'):
            dict['id']=s['id']
        elif s.has_key('__name__'):
            dict['id']=s['__name__']
        else: dict['id']='Unknown'
        dict['title']='** Expired **'

    def __save__(self):
        pass

    __inform_commit__=__save__

def initialize(app):
    initializer = AppInitializer(app)
    initializer.initialize()

class AppInitializer:
    """ Initialze an Application object (called at startup) """

    def __init__(self, app):
        self.app = (app,)

    def getApp(self):
        # this is probably necessary, but avoid acquisition anyway
        return self.app[0]

    def commit(self, note):
        get_transaction().note(note)
        get_transaction().commit()
        
    def initialize(self):
        app = self.getApp()
        # make sure to preserve relative ordering of calls below.
        self.install_cp_and_products()
        self.install_tempfolder_and_sdc()
        self.install_session_data_manager()
        self.install_browser_id_manager()
        self.install_required_roles()
        self.install_zglobals()
        self.install_inituser()
        self.install_errorlog()
        self.install_products() 
        self.install_standards()
        self.check_zglobals()

    def install_cp_and_products(self):
        app = self.getApp()

        # Ensure that Control Panel exists.
        if not hasattr(app, 'Control_Panel'):
            cpl=ApplicationManager()
            cpl._init()
            app._setObject('Control_Panel', cpl)
            self.commit('Added Control_Panel')
        
        # b/c: Ensure that a ProductFolder exists.
        if not hasattr(aq_base(app.Control_Panel), 'Products'):
            app.Control_Panel.Products=App.Product.ProductFolder()
            self.commit('Added Control_Panel.Products')

    def install_tempfolder_and_sdc(self):
        app = self.getApp()
        from Products.ZODBMountPoint.MountedObject import manage_addMounts,\
             MountedObject
        from Products.ZODBMountPoint.MountedObject import getConfiguration as \
             getDBTabConfiguration

        dbtab_config = getDBTabConfiguration()

        tf = getattr(app, 'temp_folder', None)

        if getattr(tf, 'meta_type', None) == MountedObject.meta_type:
            # tf is a MountPoint object.  This means that the temp_folder
            # couldn't be mounted properly (the meta_type would have been
            # the meta type of the container class otherwise).  The
            # MountPoint object writes a message to zLOG so we don't
            # need to.
            return

        if tf is None:
            # do nothing if we've already installed one
            if not app._getInitializerFlag('temp_folder'):
                if dbtab_config is None:
                    # DefaultConfiguration, do nothing
                    return
                mount_paths = [ x[0] for x in dbtab_config.listMountPaths() ]
                if not '/temp_folder' in mount_paths:
                    # we won't be able to create the mount point properly
                    LOG('Zope Default Object Creation', ERROR,
                        ('Could not initialze a Temporary Folder because '
                         'a database was not configured to be mounted at '
                         'the /temp_folder mount point'))
                    return
                try:
                    manage_addMounts(app, ('/temp_folder',))
                    app._setInitializerFlag('temp_folder')
                    self.commit('Added temp_folder')
                    tf = app.temp_folder
                except:
                    LOG('Zope Default Object Creation', ERROR,
                        ('Could not add a /temp_folder mount point due to an '
                        'error.'),
                        error=sys.exc_info())
                    return

        # Ensure that there is a transient object container in the temp folder
        config = getConfiguration()

        if not hasattr(aq_base(tf), 'session_data'):
            from Products.Transience.Transience import TransientObjectContainer
            addnotify = getattr(config, 'session_add_notify_script_path', None)
            delnotify = getattr(config, 'session_delete_notify_script_path',
                                None)
            default_limit = 1000
            limit = (getattr(config, 'maximum_number_of_session_objects', None)
                     or default_limit)
            timeout_spec = getattr(config, 'session_timeout_minutes', None)

            if addnotify and app.unrestrictedTraverse(addnotify, None) is None:
                LOG('Zope Default Object Creation', WARNING,
                    ('failed to use nonexistent "%s" script as '
                     'session-add-notify-script-path' % addnotify))
                addnotify=None

            if delnotify and app.unrestrictedTraverse(delnotify, None) is None:
                LOG('Zope Default Object Creation', WARNING,
                    ('failed to use nonexistent "%s" script as '
                     'session-delete-notify-script-path' % delnotify))
                delnotify=None

            toc = TransientObjectContainer(
                'session_data', 'Session Data Container',
                addNotification = addnotify,
                delNotification = delnotify,
                limit=limit)

            if timeout_spec:
                toc = TransientObjectContainer('session_data',
                                               'Session Data Container',
                                               timeout_mins = timeout_spec,
                                               addNotification = addnotify,
                                               delNotification = delnotify,
                                               limit=limit)

            tf._setObject('session_data', toc)
            tf_reserved = getattr(tf, '_reserved_names', ())
            if 'session_data' not in tf_reserved:
                tf._reserved_names = tf_reserved + ('session_data',)
            self.commit('Added session_data to temp_folder')
            return tf # return the tempfolder object for test purposes

    def install_browser_id_manager(self):
        app = self.getApp()
        if app._getInitializerFlag('browser_id_manager'):
            # do nothing if we've already installed one
            return
        # Ensure that a browser ID manager exists
        if not hasattr(app, 'browser_id_manager'):
            from Products.Sessions.BrowserIdManager import BrowserIdManager
            bid = BrowserIdManager('browser_id_manager', 'Browser Id Manager')
            app._setObject('browser_id_manager', bid)
            app._setInitializerFlag('browser_id_manager')
            self.commit('Added browser_id_manager')

    def install_session_data_manager(self):
        app = self.getApp()
        if app._getInitializerFlag('session_data_manager'):
            # do nothing if we've already installed one
            return
        # Ensure that a session data manager exists
        if not hasattr(app, 'session_data_manager'):
            from Products.Sessions.SessionDataManager import SessionDataManager
            sdm = SessionDataManager('session_data_manager',
                title='Session Data Manager',
                path='/temp_folder/session_data',
                requestName='SESSION')
            app._setObject('session_data_manager', sdm)
            app._setInitializerFlag('session_data_manager')
            self.commit('Added session_data_manager')

    def install_required_roles(self):
        app = self.getApp()
        
        # Ensure that Owner role exists.
        if hasattr(app, '__ac_roles__') and not ('Owner' in app.__ac_roles__):
            app.__ac_roles__=app.__ac_roles__ + ('Owner',)
            self.commit('Added Owner role')

        # ensure the Authenticated role exists.
        if hasattr(app, '__ac_roles__'):
            if not 'Authenticated' in app.__ac_roles__:
                app.__ac_roles__=app.__ac_roles__ + ('Authenticated',)
                self.commit('Added Authenticated role')

    def install_zglobals(self):
        app = self.getApp()

        # Make sure we have ZGlobals
        root=app._p_jar.root()
        if not root.has_key('ZGlobals'):
            from BTrees.OOBTree import OOBTree
            root['ZGlobals'] = OOBTree()
            self.commit('Added ZGlobals')

    def install_inituser(self):
        app = self.getApp()

        # Install the initial user.
        if hasattr(app, 'acl_users'):
            users = app.acl_users
            if hasattr(users, '_createInitialUser'):
                app.acl_users._createInitialUser()
                self.commit('Created initial user')

    def install_errorlog(self):
        app = self.getApp()
        if app._getInitializerFlag('error_log'):
            # do nothing if we've already installed one
            return

        # Install an error_log
        if not hasattr(app, 'error_log'):
            from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
            error_log = SiteErrorLog()
            app._setObject('error_log', error_log)
            app._setInitializerFlag('error_log')
            self.commit('Added site error_log at /error_log')

    def check_zglobals(self):
        if not doInstall():
            return

        app = self.getApp()

        # Check for dangling pointers (broken zclass dependencies) in the
        # global class registry. If found, rebuild the registry. Note that
        # if the check finds problems but fails to successfully rebuild the
        # registry we abort the transaction so that we don't leave it in an
        # indeterminate state.

        did_fixups=0
        bad_things=0
        try:
            if app.checkGlobalRegistry():
                LOG('Zope', INFO,
                    'Beginning attempt to rebuild the global ZClass registry.')
                app.fixupZClassDependencies(rebuild=1)
                did_fixups=1
                LOG('Zope', INFO,
                    'The global ZClass registry has successfully been rebuilt.')
                get_transaction().note('Rebuilt global product registry')
                get_transaction().commit()
        except:
            bad_things=1
            LOG('Zope', ERROR, 'The attempt to rebuild the registry failed.',
                error=sys.exc_info())
            get_transaction().abort()

        # Now we need to see if any (disk-based) products were installed
        # during intialization. If so (and the registry has no errors),
        # there may still be zclasses dependent on a base class in the
        # newly installed product that were previously broken and need to
        # be fixed up. If any really Bad Things happened (dangling pointers
        # were found in the registry but it couldn't be rebuilt), we don't
        # try to do anything to avoid making the problem worse.
        if (not did_fixups) and (not bad_things):

            # App.Product.initializeProduct will set this if a disk-based
            # product was added or updated and we are not a ZEO client.
            if getattr(Globals, '__disk_product_installed__', None):
                try:
                    LOG('Zope', INFO,
                        ('New disk product detected, determining if we need '
                        'to fix up any ZClasses.'))
                    if app.fixupZClassDependencies():
                        LOG('Zope',INFO,
                            'Repaired broken ZClass dependencies.')
                        self.commit('Repaired broked ZClass dependencies')
                except:
                    LOG('Zope', ERROR,
                        ('Attempt to fixup ZClass dependencies after '
                         'detecting an updated disk-based product failed.'),
                        error=sys.exc_info())
                    get_transaction().abort()

    def install_products(self):
        app = self.getApp()
        # this defers to a function for b/c reasons
        return install_products(app)

    def install_standards(self):
        app = self.getApp()
        # this defers to a  function for b/c reasons
        return install_standards(app)

def install_products(app):
    # Install a list of products into the basic folder class, so
    # that all folders know about top-level objects, aka products

    folder_permissions = get_folder_permissions()
    meta_types=[]
    done={}

    debug_mode = App.config.getConfiguration().debug_mode

    get_transaction().note('Prior to product installs')
    get_transaction().commit()

    products = get_products()

    for priority, product_name, index, product_dir in products:
        # For each product, we will import it and try to call the
        # intialize() method in the product __init__ module. If
        # the method doesnt exist, we put the old-style information
        # together and do a default initialization.
        if done.has_key(product_name):
            continue
        done[product_name]=1
        install_product(app, product_dir, product_name, meta_types,
                        folder_permissions, raise_exc=debug_mode)

    Products.meta_types=Products.meta_types+tuple(meta_types)
    Globals.default__class_init__(Folder.Folder)

def get_products():
    """ Return a list of tuples in the form:
    [(priority, dir_name, index, base_dir), ...] for each Product directory
    found, sort before returning """
    products = []
    i = 0
    for product_dir in Products.__path__:
        product_names=os.listdir(product_dir)
        for name in product_names:
            fullpath = os.path.join(product_dir, name)
            # Products must be directories
            if os.path.isdir(fullpath):
                # Products must be directories with an __init__.py[co]
                if ( os.path.exists(os.path.join(fullpath, '__init__.py')) or
                     os.path.exists(os.path.join(fullpath, '__init__.pyo')) or
                     os.path.exists(os.path.join(fullpath, '__init__.pyc')) ):
                    # import PluginIndexes 1st (why?)
                    priority = (name != 'PluginIndexes') 
                    # i is used as sort ordering in case a conflict exists
                    # between Product names.  Products will be found as
                    # per the ordering of Products.__path__
                    products.append((priority, name, i, product_dir))
        i = i + 1
    products.sort()
    return products

def import_products():
    # Try to import each product, checking for and catching errors.
    done={}

    products = get_products()
    debug_mode = App.config.getConfiguration().debug_mode

    for priority, product_name, index, product_dir in products:
        if done.has_key(product_name):
            LOG('OFS.Application', WARNING, 'Duplicate Product name',
                'After loading Product %s from %s,\n'
                'I skipped the one in %s.\n' % (
                `product_name`, `done[product_name]`, `product_dir`) )
            continue
        done[product_name]=product_dir
        import_product(product_dir, product_name, raise_exc=debug_mode)
    return done.keys()

def import_product(product_dir, product_name, raise_exc=0, log_exc=1):
    path_join=os.path.join
    isdir=os.path.isdir
    exists=os.path.exists
    _st=type('')
    global_dict=globals()
    silly=('__doc__',)
    modules=sys.modules
    have_module=modules.has_key

    try:
        package_dir=path_join(product_dir, product_name)
        if not isdir(package_dir): return
        if not exists(path_join(package_dir, '__init__.py')):
            if not exists(path_join(package_dir, '__init__.pyc')):
                if not exists(path_join(package_dir, '__init__.pyo')):
                    return

        pname="Products.%s" % product_name
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


def get_folder_permissions():
    folder_permissions={}
    for p in Folder.Folder.__ac_permissions__:
        permission, names = p[:2]
        folder_permissions[permission]=names
    return folder_permissions


def install_product(app, product_dir, product_name, meta_types,
                    folder_permissions, raise_exc=0, log_exc=1):

    path_join=os.path.join
    isdir=os.path.isdir
    exists=os.path.exists
    DictType=type({})
    global_dict=globals()
    silly=('__doc__',)

    if 1:  # Preserve indentation for diff :-)
        package_dir=path_join(product_dir, product_name)
        __traceback_info__=product_name
        if not isdir(package_dir): return
        if not exists(path_join(package_dir, '__init__.py')):
            if not exists(path_join(package_dir, '__init__.pyc')):
                if not exists(path_join(package_dir, '__init__.pyo')):
                    return
        try:
            product=__import__("Products.%s" % product_name,
                               global_dict, global_dict, silly)

            # Install items into the misc_ namespace, used by products
            # and the framework itself to store common static resources
            # like icon images.
            misc_=pgetattr(product, 'misc_', {})
            if misc_:
                if type(misc_) is DictType:
                    misc_=Misc_(product_name, misc_)
                Application.misc_.__dict__[product_name]=misc_

            # Here we create a ProductContext object which contains
            # information about the product and provides an interface
            # for registering things like classes and help topics that
            # should be associated with that product. Products are
            # expected to implement a method named 'initialize' in
            # their __init__.py that takes the ProductContext as an
            # argument.
            productObject=App.Product.initializeProduct(
                product, product_name, package_dir, app)
            context=ProductContext(productObject, app, product)

            # Look for an 'initialize' method in the product. If it does
            # not exist, then this is an old product that has never been
            # updated. In that case, we will analyze the product and
            # build up enough information to do initialization manually.
            initmethod=pgetattr(product, 'initialize', None)
            if initmethod is not None:
                initmethod(context)

            # Support old-style product metadata. Older products may
            # define attributes to name their permissions, meta_types,
            # constructors, etc.
            permissions={}
            new_permissions={}
            for p in pgetattr(product, '__ac_permissions__', ()):
                permission, names, default = (
                    tuple(p)+('Manager',))[:3]
                if names:
                    for name in names:
                        permissions[name]=permission
                elif not folder_permissions.has_key(permission):
                    new_permissions[permission]=()

            for meta_type in pgetattr(product, 'meta_types', ()):
                # Modern product initialization via a ProductContext
                # adds 'product' and 'permission' keys to the meta_type
                # mapping. We have to add these here for old products.
                pname=permissions.get(meta_type['action'], None)
                if pname is not None:
                    meta_type['permission']=pname
                meta_type['product']=productObject.id
                meta_type['visibility'] = 'Global'
                meta_types.append(meta_type)

            for name,method in pgetattr(
                product, 'methods', {}).items():
                if not hasattr(Folder.Folder, name):
                    setattr(Folder.Folder, name, method)
                    if name[-9:]!='__roles__': # not Just setting roles
                        if (permissions.has_key(name) and
                            not folder_permissions.has_key(
                                permissions[name])):
                            permission=permissions[name]
                            if new_permissions.has_key(permission):
                                new_permissions[permission].append(name)
                            else:
                                new_permissions[permission]=[name]

            if new_permissions:
                new_permissions=new_permissions.items()
                for permission, names in new_permissions:
                    folder_permissions[permission]=names
                new_permissions.sort()
                Folder.Folder.__ac_permissions__=tuple(
                    list(Folder.Folder.__ac_permissions__)+new_permissions)

            if not doInstall():
                get_transaction().abort()
            else:
                get_transaction().note('Installed product '+product_name)
                get_transaction().commit()

        except:
            if log_exc:
                LOG('Zope',ERROR,'Couldn\'t install %s' % product_name,
                    error=sys.exc_info())
            get_transaction().abort()
            if raise_exc:
                raise

def install_standards(app):
    # Check to see if we've already done this before
    # Don't do it twice (Casey)
    if getattr(app, '_standard_objects_have_been_added', 0):
        return

    # Install the replaceable standard objects
    from Products.PageTemplates.PageTemplateFile import PageTemplateFile
    std_dir = os.path.join(Globals.package_home(globals()), 'standard')
    wrote = 0
    for fn in os.listdir(std_dir):
        base, ext = os.path.splitext(fn)
        if ext == '.dtml':
            ob = Globals.DTMLFile(base, std_dir)
            fn = base
            if hasattr(app, fn):
                continue
            app.manage_addProduct['OFSP'].manage_addDTMLMethod(
                id=fn, file=open(ob.raw))
        elif ext in ('.pt', '.zpt'):
            ob = PageTemplateFile(fn, std_dir, __name__=fn)
            if hasattr(app, fn):
                continue
            app.manage_addProduct['PageTemplates'].manage_addPageTemplate(
                id=fn, title='', text=open(ob.filename))
        else:
            continue
        wrote = 1
        # Below is icky and sneaky since it makes these impossible to delete
        #ob.__replaceable__ = Globals.REPLACEABLE
        #setattr(Application, fn, ob)
    if wrote:
        app._standard_objects_have_been_added = 1
        get_transaction().note('Installed standard objects')
        get_transaction().commit()

def reinstall_product(app, product_name):
    folder_permissions = get_folder_permissions()
    meta_types=[]

    get_transaction().note('Prior to product reinstall')
    get_transaction().commit()

    for product_dir in Products.__path__:
        product_names=os.listdir(product_dir)
        product_names.sort()
        if product_name in product_names:
            removeProductMetaTypes(product_name)
            install_product(app, product_dir, product_name, meta_types,
                            folder_permissions, raise_exc=1, log_exc=0)
            break

    Products.meta_types=Products.meta_types+tuple(meta_types)
    Globals.default__class_init__(Folder.Folder)


def reimport_product(product_name):
    for product_dir in Products.__path__:
        product_names=os.listdir(product_dir)
        product_names.sort()
        if product_name in product_names:
            import_product(product_dir, product_name,
                           raise_exc=1, log_exc=0)
            break


def removeProductMetaTypes(pid):
    '''
    Unregisters the meta types registered by a product.
    '''
    meta_types = Products.meta_types
    new_mts = []
    changed = 0
    for meta_type in meta_types:
        if meta_type.get('product', None) == pid:
            # Remove this meta type.
            changed = 1
        else:
            new_mts.append(meta_type)
    if changed:
        Products.meta_types = tuple(new_mts)


def pgetattr(product, name, default=install_products, __init__=0):
    if not __init__ and hasattr(product, name): return getattr(product, name)
    if hasattr(product, '__init__'):
        product=product.__init__
        if hasattr(product, name): return getattr(product, name)

    if default is not install_products: return default

    raise AttributeError, name
