##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""ShardContainer implementation.
"""

import random
import time

from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.proxy import removeAllProxies

from z3c.sharding.interfaces import IShardPartition, IShardContainer


class Partition(Persistent):
    """Describes a partition in a shard"""
    implements(IShardPartition)

    def __init__(self, database_name, weight):
        self.database_name = database_name
        self.weight = weight

    def __repr__(self):
        return '%s(%r, %r)' % (
            self.__class__.__name__, self.database_name, self.weight)


class ShardContainer(BTreeContainer):
    """A shard container partitions its contents in multiple databases."""
    implements(IShardContainer)

    _part_table_timeout = 60 * 60  # seconds

    _v_part_table = None           # [Partition]
    _v_part_table_expiration = 0   # time when _v_part_table expires

    def __init__(self, shard_name):
        super(ShardContainer, self).__init__()
        self._shard_name = shard_name
        self._partitions = ()  # (Partition,)
        self._auto_weight = True

    def set_partitions(self, partitions):
        """Replace the partition list.

        The partitions argument holds a list of IShardPartition objects.
        """
        for part in partitions:
            assert IShardPartition.providedBy(part)
        self._partitions = tuple(partitions)
        self._v_part_table = None
        self._get_part_table()  # test the new configuration

    def get_partitions(self):
        return self.partitions

    partitions = property(get_partitions, set_partitions)

    def set_auto_weight(self, auto_weight):
        """Configure whether the automatic weighting feature is enabled.

        If enabled, the weight of each partition is computed to balance
        the size of the underlying databases.  If disabled, the weight
        comes from each partition's weight attribute.
        """
        self._auto_weight = bool(auto_weight)
        self._v_part_table = None

    def get_auto_weight(self):
        return self._auto_weight

    auto_weight = property(get_auto_weight, set_auto_weight)

    def _compute_weights(self):
        """Returns [(Partition, weight)]."""
        computed_weights = []  # [(partition, weight)]
        if self._auto_weight:
            # gather the current size of all partitions
            sizes = {}
            for part in self._partitions:
                c = self._p_jar.get_connection(part.database_name)
                size = c.db().getSize()  # returns a byte count
                sizes[part.database_name] = size
            max_size = 0
            if sizes:
                max_size = max(sizes.values())
            if max_size <= 0:
                # no sizes are known, so give all partitions the same weight
                computed_weights = [(part,  0) for part in self._partitions]
            else:
                # assign partitions a weight that causes them to auto-balance
                for part in self._partitions:
                    weight = max_size - sizes[part.database_name]
                    computed_weights.append((part, weight))
        else:
            # use the manually chosen weights
            for part in self._partitions:
                computed_weights = [(part,  part.weight)
                                    for part in self._partitions]
        return computed_weights

    def _get_part_table(self):
        """Return a list of Partitions to select from.

        Partitions will often be listed more than once in order to give
        them more weight.

        The result is cached in self._v_part_table.
        """
        res = self._v_part_table
        if res is not None and time.time() < self._v_part_table_expiration:
            return self._v_part_table

        if self._p_jar is None:
            # Can't proceed until the container is stored in
            # some database.
            raise AssertionError(
                "ShardContainer is not yet added to a database")

        computed_weights = self._compute_weights()
        total_weight = 0
        for part, weight in computed_weights:
            if weight > 0:
                total_weight += weight
        if not total_weight:
            # no weights given, so give all partitions the same weight
            part_table = [part for (part, weight) in computed_weights]
        else:
            # make a table with approx. 1000 entries.
            scale = 1000.0 / total_weight
            part_table = []
            for part, weight in computed_weights:
                count = int(scale * weight)
                for i in xrange(count):
                    part_table.append(part)

        self._v_part_table = part_table
        self._v_part_table_expiration = time.time() + self._part_table_timeout

        return part_table

    def _choose_container(self):
        """Returns the container where a new object should be stored."""
        part_table = self._get_part_table()
        if not part_table:
            raise AssertionError("No partitions defined")
        part = random.choice(part_table)
        jar = self._p_jar.get_connection(part.database_name)
        root = jar.root()
        o1 = root.get('shards')
        if o1 is None:
            root['shards'] = o1 = PersistentMapping()
            jar.add(o1)
        o2 = o1.get(self._shard_name)
        if o2 is None:
            o1[self._shard_name] = o2 = BTreeContainer()
            jar.add(o2)
        return o2

    def __setitem__(self, key, value):
        if value._p_jar is not None:
            raise ValueError("Contained object is already stored")
        super(ShardContainer, self).__setitem__(key, value)
        f = self._choose_container()
        f[key] = value
        f._p_jar.add(value)

    def __delitem__(self, key):
        obj = self._SampleContainer__data[key]
        obj = removeAllProxies(obj)
        conn = obj._p_jar
        partition = conn.root()['shards'][self._shard_name]
        # Avoid triggering an event involving the partition by deleting
        # from the partition's underlying BTree.
        tree = partition._SampleContainer__data
        super(ShardContainer, self).__delitem__(key)
        del tree[key]
