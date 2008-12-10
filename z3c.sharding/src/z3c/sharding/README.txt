===========================
Container Database Sharding
===========================

This package provides a container that automatically partitions its contents
across multiple databases.  Objects are spread between participating databases
in order to reduce database load and increase scalability.

This code puts a master index (a BTree) in the database holding the
`ShardContainer` object.  The values in the master index are ZODB
cross-database references to objects in partitions.  Partitions are
`BTreeContainer` components.

The `ShardContainer` chooses the partition for a new object based on a weighted
random selection of partition names.  The partition names are configured in
the `ShardContainer` instance.  `ShardContainer` expects the multi-database
configuration to be set up ahead of time.

See the tests below for further details.

  >>> from zope.interface.verify import verifyClass
  >>> from transaction import commit, abort
  >>> from z3c.sharding.interfaces import IShardPartition, IShardContainer
  >>> from z3c.sharding.container import Partition, ShardContainer
  >>> verifyClass(IShardPartition, Partition)
  True
  >>> verifyClass(IShardContainer, ShardContainer)
  True

Manually create a partition and verify its representation.

  >>> p1 = Partition('p1', 1.0)
  >>> print p1
  Partition('p1', 1.0)

Create a multi-database out of DemoStorages.  A multi-database is a set of
ZODB DB objects linked by a common 'databases' map.  Objects stored
in multi-databases can freely cross database boundaries.

  >>> from ZODB.DemoStorage import DemoStorage
  >>> from ZODB.DB import DB
  >>> databases = {}
  >>> for name in ('p1', 'p2', 'p3'):
  ...     db = DB(DemoStorage(), database_name=name, databases=databases)
  >>> main_db = DB(DemoStorage(), database_name='main', databases=databases)
  >>> conn = main_db.open()

Create a ShardContainer named "things" with a shard name of "things000".
The shard name must be globally unique, but the shard name
can be distinct from the container's __name__ attribute.

  >>> things = ShardContainer('things000')
  >>> conn.root()['things'] = things
  >>> commit()

A partition is required before storing anything.

  >>> from zope.app.container.btree import BTreeContainer
  >>> things['x'] = BTreeContainer()
  Traceback (most recent call last):
  ...
  AssertionError: No partitions defined

Set up a partition for the "things" contianer.

  >>> parts = []
  >>> for name in ['p1']:
  ...     parts.append(Partition(name, 0))
  >>> things.partitions = parts

Add 1 item to the container.  The item should be a `Persistent` obejct and
should implement the `IContained` interface.

  >>> thing = BTreeContainer()
  >>> thing.attr = 'value'
  >>> things['0'] = thing
  >>> thing._p_jar.db().database_name
  'p1'
  >>> things._p_jar.db().database_name
  'main'

Commit.

  >>> things._p_changed
  True
  >>> commit()
  >>> thing._p_changed
  False
  >>> things._p_changed
  False

Verify it's possible to load the thing from a new connection.

  >>> conn2 = main_db.open()
  >>> things2 = conn2.root()['things']
  >>> thing2 = things2['0']
  >>> things2._p_changed
  False
  >>> thing2.attr
  'value'
  >>> thing2._p_changed
  False
  >>> thing2._p_jar.db().database_name
  'p1'
  >>> things2._p_jar.db().database_name
  'main'
  >>> conn2.close()

Enable another partition.  Assign p1 a weight of 1 and p2 a weight of 0,
but note that the manual weights will be ignored until automatic
weighting is disabled.

  >>> parts = []
  >>> for name in ['p1', 'p2']:
  ...     parts.append(Partition(name, 2 - int(name[1])))
  >>> things.partitions = parts

Add another object.  Automatic weighting should cause the new object to always
land in the new partition.

  >>> stuff = BTreeContainer()
  >>> things['1'] = stuff
  >>> stuff._p_jar.db().database_name
  'p2'

Apply manual weighting.  Partition `p1` has weight 1 and `p2` has weight 0,
so `p1` should get everything.

  >>> things.auto_weight = False
  >>> stuff = BTreeContainer()
  >>> things['2'] = stuff
  >>> stuff._p_jar.db().database_name
  'p1'

Verify all of the objects can be found directly in the partitions.

  >>> conn.get_connection('p1').root()['shards'].keys()
  ['things000']
  >>> conn.get_connection('p2').root()['shards'].keys()
  ['things000']
  >>> sorted(conn.get_connection('p1').root()['shards']['things000'].keys())
  [u'0', u'2']
  >>> sorted(conn.get_connection('p2').root()['shards']['things000'].keys())
  [u'1']

Delete an object from the shard container, which should cause
the same object to be deleted from its partition.

  >>> del things['0']
  >>> sorted(conn.get_connection('p1').root()['shards']['things000'].keys())
  [u'2']
  >>> commit()

Clean up.

  >>> abort()
  >>> conn.close()
  >>> for database in databases.values():
  ...     database.close()
