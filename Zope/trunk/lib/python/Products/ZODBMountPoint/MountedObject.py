##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""DBTab mount point (stored in ZODB).

$Id: MountedObject.py,v 1.3 2004/02/25 18:29:58 jeremy Exp $
"""

import os

import Globals
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl.ZopeGuards import guarded_getattr
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Mount import MountPoint


_www = os.path.join(os.path.dirname(__file__), 'www')

def getConfiguration():
    from App.config import getConfiguration
    return getConfiguration().dbtab

class SimpleTrailblazer:
    """Follows Zope paths.  If a path is not found, creates a Folder.

    Respects Zope security.
    """

    restricted = 1

    def __init__(self, base):
        self.base = base

    def _construct(self, context, id, final):
        """Creates and returns the named folder."""
        dispatcher = guarded_getattr(context, 'manage_addProduct')['OFSP']
        factory = guarded_getattr(dispatcher, 'manage_addFolder')
        factory(id)
        o = context.restrictedTraverse(id)
        # Commit a subtransaction to assign the new object to
        # the correct database.
        get_transaction().commit(1)
        return o

    def traverseOrConstruct(self, path, omit_final=0):
        """Traverses a path, constructing it if necessary."""
        container = self.base
        parts = filter(None, path.split('/'))
        if omit_final:
            if len(parts) < 1:
                raise ValueError, 'Path %s is not a valid mount path' % path
            parts = parts[:-1]
        for part in parts:
            try:
                if self.restricted:
                    container = container.restrictedTraverse(part)
                else:
                    container = container.unrestrictedTraverse(part)
            except (KeyError, AttributeError):
                # Try to create a container in this place.
                container = self._construct(container, part)
        return container

    
class CustomTrailblazer (SimpleTrailblazer):
    """Like SimpleTrailblazer but creates custom objects.

    Does not respect Zope security because this may be invoked before
    security and products get initialized.
    """

    restricted = 0

    def __init__(self, base, container_class=None):
        self.base = base
        if not container_class:
            container_class = 'OFS.Folder.Folder'
        pos = container_class.rfind('.')
        if pos < 0:
            raise ValueError("Not a valid container_class: %s" % repr(
                container_class))
        self.module_name = container_class[:pos]
        self.class_name = container_class[pos + 1:]

    def _construct(self, context, id):
        """Creates and returns the named object."""
        jar = self.base._p_jar
        klass = jar.db()._classFactory(jar, self.module_name, self.class_name)
        obj = klass(id)
        obj._setId(id)
        context._setObject(id, obj)
        obj = context.unrestrictedTraverse(id)
        # Commit a subtransaction to assign the new object to
        # the correct database.
        get_transaction().commit(1)
        return obj


class MountedObject(MountPoint, SimpleItem):
    '''A MountPoint with a basic interface for displaying the
    reason the database did not connect.
    '''
    meta_type = 'ZODB Mount Point'
    _isMountedObject = 1
    _create_mount_points = 0

    icon = 'p_/broken'
    manage_options = ({'label':'Traceback', 'action':'manage_traceback'},)
    _v_mount_params = None

    manage_traceback = PageTemplateFile('mountfail.pt', _www)

    def __init__(self, path):
        path = str(path)
        self._path = path
        id = path.split('/')[-1]
        MountPoint.__init__(self, id)

    def mount_error_(self):
        return self._v_connect_error

    def _getDB(self):
        """Hook for getting the DB object for this mount point.
        """
        return getConfiguration().getDatabase(self._path)

    def _getDBName(self):
        """Hook for getting the name of the database for this mount point.
        """
        return getConfiguration().getDatabaseFactory(self._path).getName()

    def _getRootDBName(self):
        """Hook for getting the name of the root database.
        """
        return getConfiguration().getDatabaseFactory('/').getName()

    def _loadMountParams(self):
        factory = getConfiguration().getDatabaseFactory(self._path)
        params = factory.getMountParams(self._path)
        self._v_mount_params = params
        return params

    def _traverseToMountedRoot(self, root, mount_parent):
        """Hook for getting the object to be mounted.
        """
        params = self._v_mount_params
        if params is None:
            params = self._loadMountParams()
        real_root, real_path, container_class = params
        if real_root is None:
            real_root = 'Application'
        try:
            obj = root[real_root]
        except KeyError:
            if container_class or self._create_mount_points:
                # Create a database automatically.
                from OFS.Application import Application
                obj = Application()
                root[real_root] = obj
                # Get it into the database
                get_transaction().commit(1)
            else:
                raise

        if real_path is None:
            real_path = self._path
        if real_path and real_path != '/':
            try:
                obj = obj.unrestrictedTraverse(real_path)
            except (KeyError, AttributeError):
                if container_class or self._create_mount_points:
                    blazer = CustomTrailblazer(obj, container_class)
                    obj = blazer.traverseOrConstruct(real_path)
                else:
                    raise
        return obj

Globals.InitializeClass(MountedObject)


def getMountPoint(ob):
    """Gets the mount point for a mounted object.

    Returns None if the object is not a mounted object.
    """
    container = aq_parent(aq_inner(ob))
    mps = getattr(container, '_mount_points', None)
    if mps:
        mp = mps.get(ob.getId())
        if mp is not None and (mp._p_jar is ob._p_jar or ob._p_jar is None):
            # Since the mount point and the mounted object are from
            # the same connection, the mount point must have been
            # replaced.  The object is not mounted after all.
            return None
        # else the object is mounted.
        return mp
    return None


def setMountPoint(container, id, mp):
    mps = getattr(container, '_mount_points', None)
    if mps is None:
        container._mount_points = {id: aq_base(mp)}
    else:
        container._p_changed = 1
        mps[id] = aq_base(mp)


manage_addMountsForm = PageTemplateFile('addMountsForm.pt', _www)

def manage_getMountStatus(dispatcher):
    """Returns the status of each mount point specified by dbtab.conf.
    """
    res = []
    conf = getConfiguration()
    items = conf.listMountPaths()
    items.sort()
    root = dispatcher.getPhysicalRoot()
    for path, name in items:
        if not path or path == '/':
            # Ignore the root mount.
            continue
        o = root.unrestrictedTraverse(path, None)
        # Examine the _v_mount_point_ attribute to verify traversal
        # to the correct mount point.
        if o is None:
            exists = 0
            status = 'Ready to create'
        elif getattr(o, '_isMountedObject', 0):
            # Oops, didn't actually mount!
            exists = 1
            t, v = o._v_connect_error[:2]
            status = '%s: %s' % (t, v)
        else:
            exists = 1
            mp = getMountPoint(o)
            if mp is None:
                mp_old = getattr(o, '_v_mount_point_', None)
                if mp_old is not None:
                    # Use the old method of accessing mount points
                    # to update to the new method.
                    # Update the container right now.
                    setMountPoint(dispatcher.this(), o.getId(), mp_old[0])
                    status = 'Ok (updated)'
                else:
                    status = '** Something is in the way **'
            else:
                mp_path = getattr(mp, '_path', None)
                if mp_path != path:
                    status = '** Set to wrong path: %s **' % repr(mp_path)
                else:
                    status = 'Ok'
        res.append({
            'path': path, 'name': name, 'exists': exists,
            'status': status,
            })
    return res


def manage_addMounts(dispatcher, paths=(), create_mount_points=0,
                     REQUEST=None):
    """Adds MountedObjects at the requested paths.
    """
    count = 0
    app = dispatcher.getPhysicalRoot()
    for path in paths:
        mo = MountedObject(path)
        mo._create_mount_points = not not create_mount_points
        # Raise an error now if there is any problem.
        mo._test(app)
        blazer = SimpleTrailblazer(app)
        container = blazer.traverseOrConstruct(path, omit_final=1)
        container._p_jar.add(mo)
        loaded = mo.__of__(container)

        # Add a faux object to avoid generating manage_afterAdd() events
        # while appeasing OFS.ObjectManager._setObject(), then discreetly
        # replace the faux object with a MountedObject.
        faux = Folder()
        faux.id = mo.id
        faux.meta_type = loaded.meta_type
        container._setObject(faux.id, faux)
        del mo._create_mount_points
        container._setOb(faux.id, mo)
        setMountPoint(container, faux.id, mo)
        count += 1
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(
            REQUEST['URL1'] + ('/manage_main?manage_tabs_message='
            'Added %d mount points.' % count))

