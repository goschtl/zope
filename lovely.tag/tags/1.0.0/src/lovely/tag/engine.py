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
import zope.interface
from zope import component
from BTrees import IOBTree, OOBTree
import random

from zope.app.container import contained
from zope.app.intid.interfaces import IIntIdRemovedEvent, IIntIds
from lovely.tag import interfaces, tag
from zope.dottedname.resolve import resolve
import types

class TaggingEngine(persistent.Persistent, contained.Contained):
    zope.interface.implements(interfaces.ITaggingEngine,
                              interfaces.ITaggingStatistics)

    _v_nextid = None
    
    def __init__(self):
        super(TaggingEngine, self).__init__()
        self._reset()

    def _generateId(self):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = random.randrange(0, 2**31)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self._tagid_to_obj:
                return uid
            self._v_nextid = None

    def _add(self, tagObj):
        uid = self._generateId()
        self._tagid_to_obj[uid] = tagObj
        # set the __parent__ in order to get a _p_oid for the object
        #tagObj.__parent__ = self
        return uid

    def _reset(self):
        # mapping of tagid to tag object
        self._tagid_to_obj = IOBTree.IOBTree()
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
        tags_tags = set()
        for t in tags:
            tags_tags.update(self._name_to_tagids.get(t, ()))
        old_tag_ids = tags_item.intersection(tags_user)
        # any tags of the same user/item that are not in tags
        old_tag_ids = old_tag_ids.difference(tags_tags)
            
        old_tags = set([self._tagid_to_obj[id]
                        for id in old_tag_ids])

        new_tags = set([tag.Tag(item, user, tagName)
                        for tagName in tags])

        add_tags = new_tags.difference(old_tags)
        
        add_tag_ids = []
        for tagObj in add_tags:
            id = self._add(tagObj)
            add_tag_ids.append(id)
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
        del_tag_ids = old_tag_ids.difference(add_tag_ids)
        self._delTags(del_tag_ids)

    def _delTags(self, del_tag_ids):
        """deletes tags in iterable"""
        for id in del_tag_ids:
            tagObj = self._tagid_to_obj[id]
            self._user_to_tagids[tagObj.user].remove(id)
            if not len(self._user_to_tagids[tagObj.user]):
                del self._user_to_tagids[tagObj.user]

            self._item_to_tagids[tagObj.item].remove(id)
            if not len(self._item_to_tagids[tagObj.item]):
                del self._item_to_tagids[tagObj.item]

            self._name_to_tagids[tagObj.name].remove(id)
            if not len(self._name_to_tagids[tagObj.name]):
                del self._name_to_tagids[tagObj.name]
            del self._tagid_to_obj[id]

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
        self._delTags(tags)

    def getTags(self, items=None, users=None):
        """See interfaces.ITaggingEngine"""
        if items is None and users is None:
            # shortcut
            return set(self._name_to_tagids.keys())

        result = self.getTagObjects(items, users)
        return set([tag.name for tag in result])

    def _getTagIds(self, items=None, users=None, tags=None):
        if items is None and users is None and tags is None:
            # get them all
            result = set()
            for v in self._item_to_tagids.values():
                result.update(v)
            return result
        result = None
        for seq, bt in ((items, self._item_to_tagids),
                        (users, self._user_to_tagids),
                        (tags, self._name_to_tagids)):
            res = set()
            if seq is not None:
                for item in seq:
                    res.update(bt.get(item, set()))
                if result is not None:
                    result = result.intersection(res)
                else:
                    result = res
        return result

    def getTagObjects(self, items=None, users=None,  tags=None):
        ids = self._getTagIds(items, users, tags)
        return set([self._tagid_to_obj[id] for id in ids])

    def getItems(self, tags=None, users=None):
        """See interfaces.ITaggingEngine"""
        uids = self._getTagIds(items=None, users=users, tags=tags)
        res = set()
        for uid in uids:
            o = self._tagid_to_obj.get(uid)
            if o is not None:
                res.add(o.item)
        return res

    def getUsers(self, tags=None, items=None):
        """See interfaces.ITaggingEngine"""
        ids = self._getTagIds(items=items, users=None, tags=tags)
        return set([self._tagid_to_obj[id].user for id in ids])

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
                    tag_obj = self._tagid_to_obj[tagid]
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

    def getRelatedItems(self, item):
        tags = self.getTags([item])
        items = self.getItems(tags)
        if item in items:
            items.remove(item)
        result = []
        for otherItem in items:
            otherTags = self.getTags([otherItem])
            result.append((otherItem, len(tags.intersection(otherTags))))
        return sorted(result, key=lambda i: i[1], reverse=True)

    def getRelatedUsers(self, user):
        tags = self.getTags(users=[user])
        users = self.getUsers(tags)
        if user in users:
            users.remove(user)
        result = []
        for otherUser in users:
            otherTags = self.getTags(users=[otherUser])
            result.append((otherUser, len(tags.intersection(otherTags))))
        return sorted(result, key=lambda i: i[1], reverse=True)

    def getCloud(self, items=None, users=None):
        """See interfaces.ITaggingEngine"""
        if type(items) == types.IntType:
            items = [items]
        if type(users) in types.StringTypes:
            users = [users]

        tags = self.getTagObjects(items=items, users=users)
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
        return '<%s entries=%i>' %(self.__class__.__name__,
                                   len(self._tagid_to_obj))


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
            tagObj = self._tagid_to_obj[tagId]
            tagObj.name = new
        newTagIds = IOBTree.IOSet(self._name_to_tagids.get(new, ()))
        newTagIds.update(tagIds)
        self._name_to_tagids[new] = newTagIds
        del self._name_to_tagids[old]
        return len(tagIds)

    def normalize(self, normalizer):
        if type(normalizer) == types.StringType:
            normalizer = resolve(normalizer)
        names = list(self._name_to_tagids.keys())
        count = 0
        for name in names:
            newName = normalizer(name)
            if newName != name:
                count += self.rename(name, newName)
        return count

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
            
