##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""Datatypes for the Zope schema for use with ZConfig."""

import os
from ZODB.config import ZODBDatabase

# generic datatypes

def security_policy_implementation(value):
    value = value.upper()
    ok = ('PYTHON', 'C')
    if value not in ok:
        raise ValueError, (
            "security-policy-implementation must be one of %s" % repr(ok)
            )
    return value

def datetime_format(value):
    value = value.lower()
    ok = ('us', 'international')
    if value not in ok:
        raise ValueError, (
            "datetime-format must be one of %r" % repr(ok)
            )
    return value

def cgi_environment(section):
    return section.environ

# Datatype for the access and trace logs
# (the loghandler datatypes come from the zLOG package)

class LoggerFactory:
    """
    A factory used to create loggers while delaying actual logger
    instance construction.  We need to do this because we may want to
    reference a logger before actually instantiating it (for example,
    to allow the app time to set an effective user).  An instance of
    this wrapper is a callable which, when called, returns a logger
    object.
    """
    def __init__(self, section):
        self.name = section.getSectionName()
        self.level = section.level
        self.handler_factories = section.handlers
        self.resolved = None

    def __call__(self):
        if self.resolved is None:
            # set the logger up
            import logging
            logger = logging.getLogger(self.name)
            logger.handlers = []
            logger.propagate = 0
            logger.setLevel(self.level)
            for handler_factory in self.handler_factories:
                handler = handler_factory()
                logger.addHandler(handler)
            self.resolved = logger
        return self.resolved

# DNS resolver

def dns_resolver(hostname):
    from ZServer.medusa import resolver
    return resolver.caching_resolver(hostname)

# mount-point definition

def mount_point(value):
    if not value:
        raise ValueError, 'mount-point must not be empty'
    if not value.startswith('/'):
        raise ValueError, ("mount-point '%s' is invalid: mount points must "
                           "begin with a slash" % value)
    return value

# A datatype that converts a Python dotted-path-name to an object

def importable_name(name):
    try:
        components = name.split('.')
        start = components[0]
        g = globals()
        package = __import__(start, g, g)
        modulenames = [start]
        for component in components[1:]:
            modulenames.append(component)
            try:
                package = getattr(package, component)
            except AttributeError:
                n = '.'.join(modulenames)
                package = __import__(n, g, g, component)
        return package
    except ImportError:
        raise ValueError, (
            'The object named by "%s" could not be imported' %  name )

# A datatype that ensures that a dotted path name can be resolved but
# returns the name instead of the object

def python_dotted_path(name):
    ob = importable_name(name) # will fail in course
    return name

# Datatype for the root configuration object
# (adds the softwarehome and zopehome fields; default values for some
#  computed paths, configures dbtab)

def root_config(section):
    from ZConfig import ConfigurationError
    here = os.path.dirname(os.path.abspath(__file__))
    swhome = os.path.dirname(os.path.dirname(here))
    section.softwarehome = swhome
    section.zopehome = os.path.dirname(os.path.dirname(swhome))
    if section.cgi_environment is None:
        section.cgi_environment = {}
    if section.clienthome is None:
        section.clienthome = os.path.join(section.instancehome, "var")
    # set up defaults for pid_filename and lock_filename if they're
    # not in the config
    if section.pid_filename is None:
        section.pid_filename = os.path.join(section.clienthome, 'Z2.pid')
    if section.lock_filename is None:
        section.lock_filename = os.path.join(section.clienthome, 'Z2.lock')

    if not section.databases:
        section.databases = getDefaultDatabaseFactories(section)

    mount_factories = {} # { name -> factory}
    mount_points = {} # { virtual path -> name }
    dup_err = ('Invalid configuration: ZODB databases named "%s" and "%s" are '
               'both configured to use the same mount point, named "%s"')

    for database in section.databases:
        points = database.getVirtualMountPaths()
        name = database.config.getSectionName()
        mount_factories[name] = database
        for point in points:
            if mount_points.has_key(point):
                raise ConfigurationError(dup_err % (mount_points[point],
                                                    name, point))
            mount_points[point] = name
    from DBTab.DBTab import DBTab
    section.dbtab = DBTab(mount_factories, mount_points)

    return section

class ZopeDatabase(ZODBDatabase):
    """ A ZODB database datatype that can handle an extended set of
    attributes for use by DBTab """

    def createDB(self):
        return ZODBDatabase.open(self)

    def open(self):
        DB = self.createDB()
        if self.config.connection_class:
            # set the connection class
            DB.klass = self.config.connection_class
        if self.config.class_factory is not None:
            DB.setClassFactory(self.config.class_factory)
        from ZODB.ActivityMonitor import ActivityMonitor
        DB.setActivityMonitor(ActivityMonitor())
        return DB

    def getName(self):
        return self.name

    def getOpenAtStartup(self):
        # XXX implement
        return 0

    def computeMountPaths(self):
        mps = []
        for part in self.config.mount_points:
            real_root = None
            if ':' in part:
                # 'virtual_path:real_path'
                virtual_path, real_path = part.split(':', 1)
                if real_path.startswith('~'):
                    # Use a special root.
                    # 'virtual_path:~real_root/real_path'
                    real_root, real_path = real_path[1:].split('/', 1)
            else:
                # Virtual path is the same as the real path.
                virtual_path = real_path = part
            mps.append((virtual_path, real_root, real_path))
        return mps

    def getVirtualMountPaths(self):
        return [item[0] for item in self.computeMountPaths()]

    def getMountParams(self, mount_path):
        """Returns (real_root, real_path, container_class) for a virtual
        mount path.
        """
        for (virtual_path, real_root, real_path) in self.computeMountPaths():
            if virtual_path == mount_path:
                container_class = self.config.container_class
                if not container_class and virtual_path != '/':
                    # default to OFS.Folder.Folder for nonroot mounts
                    # if one isn't specified in the config
                    container_class = 'OFS.Folder.Folder'
                return (real_root, real_path, container_class)
        raise LookupError('Nothing known about mount path %s' % mount_path)
    
def getDefaultDatabaseFactories(context):
    # default to a filestorage named 'Data.fs' in clienthome
    # and a temporary storage for session data
    from ZODB.Connection import Connection
    from ZODB.config import FileStorage
    from Products.TemporaryFolder.config import TemporaryStorage

    l = []
    class dummy:
        def __init__(self, name, **kw):
            self.name = name
            for k, v in kw.items():
                setattr(self, k, v)

        def getSectionName(self):
            return self.name

    path = os.path.join(context.clienthome, 'Data.fs')

    fs = dummy('default filestorage at %s' % path, path=path,
                  create=None, read_only=None, quota=None)
    main = ZopeDatabase(dummy('main', storage=FileStorage(fs), cache_size=5000,
                              pool_size=7, version_pool_size=3,
                              version_cache_size=100, mount_points=['/'],
                              connection_class=Connection,
                              class_factory=None, container_class=None))

    l.append(main)

    ts = dummy('temporary storage for sessioning')
    temporary = ZopeDatabase(dummy('temporary', storage=TemporaryStorage(ts),
                                   cache_size=5000, pool_size=7,
                                   version_pool_size=3, version_cache_size=100,
                                   mount_points=['/temp_folder'],
                                   connection_class=Connection,
                                   class_factory=None,
                                   container_class=('Products.TemporaryFolder.'
                                                    'TemporaryFolder.'
                                                    'SimpleTemporaryContainer')
                                   ))
    l.append(temporary)

    return l
    

