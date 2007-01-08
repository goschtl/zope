##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Tagging Engine Implementation

$Id$
"""
__docformat__ = "reStructuredText"

import persistent
import persistent.list
import zope.interface
from zope import component
from BTrees import IOBTree, OOBTree
from zope.app.container import contained
from zope.app import intid
from zope.app.intid.interfaces import IIntIdRemovedEvent, IIntIds
from lovely.tag import interfaces, tag

class TaggingEngine(persistent.Persistent, contained.Contained):
    zope.interface.implements(interfaces.ITaggingEngine,
                              interfaces.ITaggingStatistics)
    
    def __init__(self):
        super(TaggingEngine, self).__init__()
        self._reset()

    def _reset(self):
        # Used purely to provide a persistence reference for the tag objects
        self._tags = persistent.list.PersistentList()

        # Used to generate ids for tag objects
        self._tag_ids = intid.IntIds()
        # Our indices for efficient querying
        self._user_to_tagids = OOBTree.OOBTree()
        self._item_to_tagids = IOBTree.IOBTree()
        self._name_to_tagids = OOBTree.OOBTree()

    @property
    def tagCount(self):
        return len(self._name_to_tagids)

    @property
    def itemCount(self):
        return len(self._item_to_tagids)

    @property
    def userCount(self):
        return len(self._user_to_tagids)

    def update(self, item, user, tags):
        """See interfaces.ITaggingEngine"""
        tags_item = set(self._item_to_tagids.get(item, ()))
        tags_user = set(self._user_to_tagids.get(user, ()))

        old_tag_ids = tags_item.intersection(tags_user)
            
        old_tags = set([self._tag_ids.getObject(id)
                        for id in old_tag_ids])

        new_tags = set([tag.Tag(item, user, tagName)
                        for tagName in tags])

        add_tags = new_tags.difference(old_tags)
        del_tags = old_tags.difference(new_tags)

        for tagObj in add_tags:
            self._tags.append(tagObj)
            # set the __parent__ in order to get a _p_oid for the object
            tagObj.__parent__ = self
            id = self._tag_ids.register(tagObj)

            ids = self._user_to_tagids.get(user)
            if ids is None:
                self._user_to_tagids[user] = IOBTree.IOSet((id,))
            else:
                ids.insert(id)

            ids = self._item_to_tagids.get(item)
            if ids is None:
                self._item_to_tagids[item] = IOBTree.IOSet((id,))
            else:
                ids.insert(id)

            ids = self._name_to_tagids.get(tagObj.name)
            if ids is None:
                self._name_to_tagids[tagObj.name] = IOBTree.IOSet((id,))
            else:
                ids.insert(id)

        self._delTags(del_tags)

    def _delTags(self, del_tags):
        """deletes tags in iterable"""
        for tagObj in del_tags:
            id = self._tag_ids.getId(tagObj)
            self._tag_ids.unregister(tagObj)
            self._tags.remove(tagObj)
        
            self._user_to_tagids[tagObj.user].remove(id)
            if not len(self._user_to_tagids[tagObj.user]):
                del self._user_to_tagids[tagObj.user]
        
            self._item_to_tagids[tagObj.item].remove(id)
            if not len(self._item_to_tagids[tagObj.item]):
                del self._item_to_tagids[tagObj.item]
        
            self._name_to_tagids[tagObj.name].remove(id)
            if not len(self._name_to_tagids[tagObj.name]):
                del self._name_to_tagids[tagObj.name]

    def delete(self, item=None, user=None, tag=None):
        tags = None
        if item is not None:
            tags = set(self._item_to_tagids.get(item, ()))
        if user is not None:
            user_tags = set(self._user_to_tagids.get(user, ()))
            if tags is not None:
                tags = tags.intersection(user_tags)
            else:
                tags = user_tags
        if tag is not None:
            name_tags = set(self._name_to_tagids.get(tag, ()))
            if tags is not None:
                tags = tags.intersection(name_tags)
            else:
                tags = name_tags
        # make objects
        tags = map(self._tag_ids.getObject, tags)
        self._delTags(tags)
        

    def getTags(self, items=None, users=None):
        """See interfaces.ITaggingEngine"""
        if items is None and users is None:
            # shortcut
            return set(self._name_to_tagids.keys())

        result = self._getTagObjects(items, users)
        return set([tag.name for tag in result])

    def _getTagObjects(self, items, users):

        if items is None and users is None:
            users_result = set()
            for v in self._item_to_tagids.values():
                users_result.update(v)
        
        if items is not None:
            items_result = set()
            for item in items:
                items_result.update(self._item_to_tagids.get(item, set()))
        
        if users is not None:
            users_result = set()
            for user in users:
                users_result.update(self._user_to_tagids.get(user, set()))
        
        if items is None:
            result = users_result
        elif users is None:
            result = items_result
        else:
            result = items_result.intersection(users_result)
        return set([self._tag_ids.getObject(id) for id in result])


    def getItems(self, tags=None, users=None):
        """See interfaces.ITaggingEngine"""
        if tags is None and users is None:
            return set(self._item_to_tagids.keys())

        if tags is not None:
            tags_result = set()
            for name in tags:
                tags_result.update(self._name_to_tagids.get(name, set()))

        if users is not None:
            users_result = set()
            for user in users:
                users_result.update(self._user_to_tagids.get(user, set()))

        if tags is None:
            result = users_result
        elif users is None:
            result = tags_result
        else:
            result = tags_result.intersection(users_result)

        return set([self._tag_ids.getObject(id).item for id in result])


    def getUsers(self, tags=None, items=None):
        """See interfaces.ITaggingEngine"""
        if tags is None and items is None:
            return set(self._user_to_tagids.keys())

        if tags is not None:
            tags_result = set()
            for name in tags:
                tags_result.update(self._name_to_tagids.get(name, set()))

        if items is not None:
            items_result = set()
            for item in items:
                items_result.update(self._item_to_tagids.get(item, set()))

        if tags is None:
            result = items_result
        elif items is None:
            result = tags_result
        else:
            result = tags_result.intersection(items_result)

        return set([self._tag_ids.getObject(id).user for id in result])


    def getRelatedTags(self, tag, degree=1):
        """See interfaces.ITaggingEngine"""
        result = set()
        degree_counter = 1
        previous_degree_tags = set([tag])
        degree_tags = set()
        while degree_counter <= degree:
            for cur_name in previous_degree_tags:
                tagids = self._name_to_tagids.get(cur_name, ())
                for tagid in tagids:
                    tag_obj = self._tag_ids.getObject(tagid)
                    degree_tags.update(self.getTags(
                        items=(tag_obj.item,), users=(tag_obj.user,) ))
            # After all the related tags of this degree were found, update the
            # result set and clean up the variables for the next round.
            result.update(degree_tags)
            previous_degree_tags = degree_tags
            degree_tags = set()
            degree_counter += 1
        # Make sure the original is not included
        if tag in result:
            result.remove(tag)
        return result

    def getCloud(self, items=None, users=None):
        """See interfaces.ITaggingEngine"""
        import types
        if type(items) == types.IntType:
            items = [items]
        if type(users) in types.StringTypes:
            users = [users]

        tags = self._getTagObjects(items=items, users=users)
        d = {}
        for tag in tags:
            if d.has_key(tag.name):
                d[tag.name] += 1
            else:
                d[tag.name] = 1
        return set(d.items())

    def getFrequency(self, tags):
        """See interfaces.ITaggingEngine"""
        result = {}
        for tag in tags:
            frequency = 0
            if tag in self._name_to_tagids:
                frequency = len(self._name_to_tagids[tag])
            result[tag] = frequency
        return set(result.items())

    def __repr__(self):
        return '<%s entries=%i>' %(self.__class__.__name__, len(self._tags))


    def cleanStaleItems(self):
        """clean out stale items which have no associated object"""
        intIds = zope.component.getUtility(IIntIds, context=self)
        cleaned = []
        for uid in  self.getItems():
            obj = intIds.queryObject(uid)
            if obj is None:
                self.delete(item=uid)
                cleaned.append(uid)
        return cleaned

    def rename(self, old, new):
        """rename tag @old to @new"""

        if old == new:
            return 0
        tagIds = set(self._name_to_tagids.get(old, ()))
        for tagId in tagIds:
            tagObj = self._tag_ids.getObject(tagId)
            tagObj.name = new
        newTagIds = set(self._name_to_tagids.get(new, ()))
        newTagIds.update(tagIds)
        self._name_to_tagids[new] = newTagIds
        del self._name_to_tagids[old]
        return len(tagIds)
        

@component.adapter(IIntIdRemovedEvent)
def removeItemSubscriber(event):
    
    """A subscriber to IntIdRemovedEvent which removes an item from
    the tagging engine"""
    ob = event.object
    if not interfaces.ITaggable.providedBy(ob):
        return
    for engine in zope.component.getAllUtilitiesRegisteredFor(
        interfaces.ITaggingEngine, context=ob):
        uid = zope.component.getUtility(IIntIds, context=engine).queryId(ob)
        if uid is not None:
            engine.delete(uid)
            
