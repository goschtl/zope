##############################################################################
#
# Copyright (c) 2004, 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""ZCatalog index for efficient queries of the most recent items
"""
import types

from zope.interface import implements
from AccessControl import Permissions
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl.SecurityInfo import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBucket
from BTrees.Length import Length
from App.special_dtml import DTMLFile
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.PluginIndexes.interfaces import IUniqueValueIndex
from Products.ZCatalog.Lazy import LazyMap
from zLOG import LOG
from zLOG import WARNING

_marker = []

def _getSourceValue(obj, attrname):
    """ Return the data to be indexed for obj.
    """
    value = getattr(obj, attrname)
    try:
        # Try calling it
        value = value()
    except (TypeError, AttributeError):
        pass
    return value

class RecentItemsIndex(SimpleItem):
    """ Recent items index.
    """
    implements(IUniqueValueIndex)

    meta_type = 'Recent Items Index'

    # class default;  instances get Length() in their clear()
    numObjects = lambda: 0

    manage_options = (
        {'label': 'Overview', 'action': 'manage_main'},
    )

    manage_main = DTMLFile('www/manageIndex', globals())

    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.manage_zcatalog_indexes)

    def __init__(self,
                 id,
                 field_name=None,
                 date_name=None,
                 max_length=None,
                 guard_roles=None,
                 guard_permission=None,
                 extra=None,
                 caller=None,
                ):
        """ Recent items index constructor

        id -- Zope id for index in

        field_name -- Name of attribute used to classify the objects. A
        recent item list is created for each value of this field indexed.
        If this value is omitted, then a single recent item list for all
        cataloged objects is created.

        date_name -- Name of attribute containing a date which specifies the
        object's age.

        max_length -- Maximum length of each recent items list.

        guard_roles -- A list of one or more roles that must be granted the
        guard permission in order for an object to be indexed. Ignored if
        no guard_permission value is given.

        guard_permission -- The permission that must be granted to the
        guard roles for an object in order for it to be indexed. Ignored if
        no guard_roles value is given.

        extra and caller are used by the wonderous ZCatalog addIndex
        machinery. You can ignore them, unfortunately I can't 8^/
        """
        self.id = id
        self.field_name = field_name or getattr(extra, 'field_name', None)
        self.date_name = date_name or extra.date_name
        self.max_length = max_length or extra.max_length
        assert self.max_length > 0, 'Max item length value must be 1 or greater'
        if guard_roles is None:
            guard_roles = getattr(extra, 'guard_roles', None)
        if guard_permission is None:
            guard_permission = getattr(extra, 'guard_permission', None)
        if guard_permission is not None and guard_roles:
            self.guard_permission = guard_permission
            self.guard_roles = tuple(guard_roles)
        else:
            self.guard_permission = self.guard_roles = None
        self.clear()

    ## IPluggableIndex implementation.
    def getEntryForObject(self, docid, default=None):
        """ See IPluggableIndex.
        """
        try:
            fieldvalue = self._rid2value[docid]
        except KeyError:
            return default
        for date, rid in self._value2items[fieldvalue].keys():
            if rid == docid:
                return {'value':fieldvalue, 'date':date}
        # If we get here then _rid2values is inconsistent with _value2items
        LOG('RecentItemsIndex', WARNING,
            'Field value found for item %s, but no date. '
            'This should not happen.' % docid)
        return default

    def getIndexSourceNames(self):
        """ See IPluggableIndex.
        """
        return (self.field_name,)

    def index_object(self, docid, obj, theshold=None):
        """ See IPluggableIndex.
        """
        if self.guard_permission is not None and self.guard_roles:
            allowed_roles = rolesForPermissionOn(self.guard_permission, obj)
            for role in allowed_roles:
                if role in self.guard_roles:
                    break
            else:
                # Object does not have proper permission grant
                # to be in the index
                self.unindex_object(docid)
                return 0
        try:
            if self.field_name is not None:
                fieldvalue = _getSourceValue(obj, self.field_name)
            else:
                fieldvalue = None
            datevalue = _getSourceValue(obj, self.date_name)
        except AttributeError:
            # One or the other source attributes is missing
            # unindex the object and bail
            self.unindex_object(docid)
            return 0
        datevalue = datevalue.timeTime()
        entry = self.getEntryForObject(docid)
        if (entry is None or fieldvalue != entry['value']
            or datevalue != entry['date']):
            # XXX Note that setting the date older than a previously pruned
            #     object will result in an incorrect index state. This may
            #     present a problem if dates are changed arbitrarily
            if entry is None:
                self.numObjects.change(1)
            else:
                # unindex existing entry
                self.unindex_object(docid)
            self._rid2value[docid] = fieldvalue
            try:
                items = self._value2items[fieldvalue]
            except KeyError:
                # Unseen value, create a new items bucket
                items = self._value2items[fieldvalue] = OIBucket()
            items[datevalue, docid] = docid
            while len(items) > self.max_length:
                # Prune the oldest items
                olddate, oldrid = items.minKey()
                # Unindex by hand to avoid theoretical infinite loops
                self.numObjects.change(-1)
                del items[olddate, oldrid]
                if not items:
                    # Not likely, unless max_length is 1
                    del self._value2items[fieldvalue]
                try:
                    del self._rid2value[oldrid]
                except KeyError:
                    LOG('RecentItemsIndex', WARNING,
                        'Could not unindex field value for %s.' % oldrid)
            return 1
        else:
            # Index is up to date, nothing to do
            return 0

    def unindex_object(self, docid):
        """ See IPluggableIndex.
        """
        try:
            fieldvalue = self._rid2value[docid]
        except KeyError:
            return 0 # docid not in index
        self.numObjects.change(-1)
        del self._rid2value[docid]
        items = self._value2items[fieldvalue]
        for date, rid in items.keys():
            if rid == docid:
                del items[date, rid]
                if not items:
                    del self._value2items[fieldvalue]
                return 1
        return 1

    def _apply_index(self, request, cid=''):
        """ See IPluggableIndex.
        """
        return None

    def indexSize(self):
        """ See IPluggableIndex.
        """
        return len(self._value2items)

    def clear(self):
        """ See IPluggableIndex.
        """
        self.numObjects = Length()
        # Mapping field value => top items
        self._value2items = OOBTree()
        # Mapping indexed rid => field value for unindexing
        self._rid2value = IOBTree()

    # IUniqueValueIndex implementation.
    def hasUniqueValuesFor(self, name):
        """ See IUniqueValueIndex.
        """
        return name == self.field_name

    def uniqueValues(self, name=None, withLengths=0):
        """ See IUniqueValueIndex.
        """
        if withLengths:
            return self.getItemCounts().items()

        if name is None:
            name = self.field_name
        if name == self.field_name:
            return self._value2items.keys()
        else:
            return []

    ## Index specific methods ##
    def getItemCounts(self):
        """ Return a mapping of field values => item counts.
        """
        counts = {}
        for value, items in self._value2items.items():
            counts[value] = len(items)
        return counts

    def query(self, value=None, limit=None, merge=1):
        """ Return a lazy sequence of catalog brains like a catalog search.

        Brains coorespond to the most recent items for the value(s) given.

        If 'value' is omitted, return the most recent for all values.

        The results are returned in order, newest first.
        
        'limit', if passed, must be an integer value restricting the maximum
        number of results.
        
        If no limit is specified, the indexes' maximum length is used as
        the limit.

        'merge' is a flag:  if true, return a lazy map of the brains.  If
        false, return a sequence of (value, rid, fetch) tuples which can
        be merged later.
        """
        catalog = aq_parent(aq_inner(self))
        if value is None and self.field_name is not None:
            # Query all values
            value = list(self._value2items.keys())
        elif value is not None and self.field_name is None:
            # Ignore value given if there is no classifier field
            value = None
        if isinstance(value, (types.TupleType, types.ListType)):
            # Query for multiple values
            results = []
            for fieldval in value:
                try:
                    itempairs = self._value2items[fieldval].keys()
                except KeyError:
                    pass
                else:
                    results.extend(itempairs)
            results.sort()
            if merge:
                results = [rid for date, rid in results]
            else:
                # Create triples expected by mergeResults()
                results = [(date, rid, catalog.__getitem__)
                           for date, rid in results]
        else:
            # Query for single value
            try:
                items = self._value2items[value]
            except KeyError:
                results = []
            else:
                if merge:
                    results = items.values()
                else:
                    # Create triples expected by mergeResults()
                    results = [(date, rid, catalog.__getitem__)
                               for date, rid in items.keys()]
        results.reverse()
        if limit is not None:
            results = results[:limit]
        if merge:
            return LazyMap(catalog.__getitem__, results, len(results))
        else:
            return results


InitializeClass(RecentItemsIndex)

addIndexForm = DTMLFile('www/addIndex', globals())
