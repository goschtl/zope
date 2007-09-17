=========
Relations
=========

This package provides functionality to realize relations using the
zc.relationship package.

  >>> from zope import component
  >>> from zope.app.intid.interfaces import IIntIds
  >>> intids = component.getUtility(IIntIds)


Relation Type
-------------

A relation type define the relation.

  >>> from lovely.relation.app import RelationType
  >>> relType = RelationType(u'my targets')
  >>> relType
  <RelationType u'my targets'>


Relationship
------------

By using relationships we can connect targets.

  >>> from lovely.relation.app import Relationship

First we need something to connect.

  >>> class Source(object):
  ...     def __init__(self, name):
  ...         self.name = name
  ...     def __repr__(self):
  ...         return '<%s %r>' % (self.__class__.__name__, self.name)

  >>> class Target(object):
  ...     def __init__(self, name):
  ...         self.name = name
  ...     def __repr__(self):
  ...         return '<%s %r>' % (self.__class__.__name__, self.name)

  >>> source = Source('s1')
  >>> relationship = Relationship(source, [relType], [])
  >>> relationship.sources
  <Source 's1'>

  >>> relationship.relations
  [<RelationType u'my targets'>]

  >>> [o for o in relationship.targets]
  []

Now for the more interesting part of relations we need a relation container
which holds all relations and allows queries.

  >>> from lovely.relation.app import Relations
  >>> relations = Relations()
  >>> relations.add(relationship)

  >>> [o for o in relations.findTargets(source)]
  []

The objects involved in a relation are registered in the IntIds utility.

  >>> intids = component.getUtility(IIntIds)
  >>> sourceId = intids.getId(source)
  >>> sourceId is None
  False

Let us add an target to the relationship.

  >>> target = Target('o1 of s1')
  >>> relationship.targets = [target]
  >>> targetId = intids.getId(target)
  >>> targetId is None
  False

Now we can lookup the targets again.

  >>> [o for o in relations.findTargets(source)]
  [<Target 'o1 of s1'>]

  >>> [o for o in relations.findTargetTokens(source)] == [intids.getId(target)]
  True

It is also possible to use intids for the queries.

  >>> [o for o in relations.findTargets(sourceId)]
  [<Target 'o1 of s1'>]

The above lookup returns all targets of all existing relations. If we want to
see only the targets of a specific relation then we need to provide the
relation.

  >>> [o for o in relations.findTargets(source, relType)]
  [<Target 'o1 of s1'>]
  >>> [o for o in relations.findTargets(sourceId, relType)]
  [<Target 'o1 of s1'>]

We can also ask the other way around.

  >>> [s for s in relations.findSources(target, relType)]
  [<Source 's1'>]
  >>> [s for s in relations.findSources(targetId, relType)]
  [<Source 's1'>]

  >>> [s for s in relations.findSourceTokens(target, relType)] == [intids.getId(source)]
  True

We can also ask for all target of a relation without specifying the source.

  >>> list(relations.findRelationTargets(relType))
  [<Target 'o1 of s1'>]

  >>> list(relations.findRelationTargetTokens(relType)) == [intids.getId(target)]
  True

And the same for sources.

  >>> list(relations.findRelationSources(relType))
  [<Source 's1'>]

  >>> list(relations.findRelationSourceTokens(relType)) == [intids.getId(source)]
  True

Now lets create new targets and a new relationship.

  >>> s2 = Source('s2')
  >>> o2 = Target('o2 of s2')
  >>> r2 = Relationship(s2, [relType], [target, o2])
  >>> relations.add(r2)

  >>> sorted([s for s in relations.findSources(target, relType)],
  ...        key=lambda x:x.name)
  [<Source 's1'>, <Source 's2'>]

  >>> list(relations.findRelationTargets(relType))
  [<Target 'o1 of s1'>, <Target 'o2 of s2'>]

  >>> list(relations.findRelationSources(relType))
  [<Source 's1'>, <Source 's2'>]


Relation Types
--------------

Relation types can be provided to Relations via a RelaationTypes container. The
container can then be registered as a utility.

  >>> from lovely.relation.interfaces import IRelationTypes
  >>> from lovely.relation.app import RelationTypes
  >>> types = RelationTypes()
  >>> types
  <RelationTypes None>

  >>> from zope import component
  >>> component.provideUtility(types, IRelationTypes)

Now we can put our relations into this container and use them by name.

  >>> types['my targets'] = relType
  >>> types['my targets']
  <RelationType u'my targets'>

Now we can use the relation name to lookup for reltated targets.

  >>> sorted([s for s in relations.findSources(target, 'my targets')],
  ...        key=lambda x:x.name)
  [<Source 's1'>, <Source 's2'>]


More Targets
------------

  >>> targets = []
  >>> for i in range(1000):
  ...     targets.append(Target('o%i'%i))
  >>> for i in range(5):
  ...     s = Source('s%i'%i)
  ...     r = Relationship(s, [relType], targets)
  ...     relations.add(r)

  >>> sorted([s for s in relations.findSources(targets[44], 'my targets')],
  ...        key=lambda x:x.name)
  [<Source 's0'>, <Source 's1'>, <Source 's2'>, <Source 's3'>, <Source 's4'>]


Optimized Relationship for One To Many Relation
-----------------------------------------------

A predefined one to many relationship using a btree to store and retrieve the
many relation.

  >>> from lovely.relation.app import OneToManyRelationship
  >>> otmSource = Source(u'otm source')
  >>> relType = RelationType(u'otm relation')
  >>> types[u'otm relation'] = relType
  >>> otm = OneToManyRelationship(otmSource, [relType])
  >>> otm.sources
  <Source u'otm source'>

  >>> otm.relations
  [<RelationType u'otm relation'>]

  >>> [o for o in otm.targets]
  []

The one to many relationship provides an extended interface.

  >>> from lovely.relation.interfaces import IOneToManyRelationship
  >>> IOneToManyRelationship.providedBy(otm)
  True

This interface allows us to add and remove targets.

  >>> otmTarget = Target(u'otm obj 1')
  >>> otm.add(otmTarget)
  >>> [o for o in otm.targets]
  [<Target u'otm obj 1'>]

We put the relationship into our relations container.

  >>> relations.add(otm)
  >>> sorted([s for s in relations.findSources(otmTarget, 'otm relation')])
  [<Source u'otm source'>]

  >>> otm.remove(otmTarget)
  >>> [o for o in otm.targets]
  []


Access To Relationships
-----------------------

  >>> target44 = targets[44]
  >>> targetRelations = list(relations.findTargetRelationships(target44))
  >>> len(targetRelations)
  5

  >>> source = targetRelations[0].sources
  >>> source
  <Source 's0'>

  >>> sourceRelations = list(relations.findSourceRelationships(source))
  >>> len(sourceRelations)
  1

  >>> len(sourceRelations[0].targets)
  1000

  >>> target44 in sourceRelations[0].targets
  True


More Relations
--------------

A relationship can belong to more than just one relation type. First we need a
new relation type. This time we do not add the type to the relation types
container.

  >>> otherRelType = RelationType(u'my other targets')
  >>> otherRelType
  <RelationType u'my other targets'>

  >>> rel = targetRelations[0]
  >>> rel.addRelation(otherRelType)

Now we lookup the source for relation 'my targets'.

  >>> sorted([s for s in relations.findSources(target44, 'my targets')],
  ...        key=lambda x:x.name)
  [<Source 's0'>, <Source 's1'>, <Source 's2'>, <Source 's3'>, <Source 's4'>]

Now we can also lookup the sources for the new relation.

  >>> sorted([s for s in relations.findSources(target44, 'my other targets')],
  ...        key=lambda x:x.name)
  Traceback (most recent call last):
  ...
  KeyError: 'my other targets'

We get a KeyError because our new source is not stored in the relation types
container, but if we use the relation type target we get the result.

  >>> sorted([s for s in relations.findSources(target44, otherRelType)],
  ...        key=lambda x:x.name)
  [<Source 's0'>]

And let's remove the relation.

  >>> rel.removeRelation(otherRelType)
  >>> sorted([s for s in relations.findSources(target44, otherRelType)],
  ...        key=lambda x:x.name)
  []


More Relation Types
-------------------

Subclasses of Relationship and Relations can control which container relation
types are looked up in by overriding the `relationtypes` property.

  >>> from zope import interface
  >>> from zope import component
  >>> from lovely.relation.app import OneToOneRelationship
  >>> from lovely.relation.app import OneToOneRelationships

  >>> class IMyTypes(interface.Interface):
  ...     pass

  >>> class MyTypes(RelationTypes):
  ...     interface.implements(IMyTypes)

  >>> mytypes = MyTypes()
  >>> mytypes[u'foo'] = RelationType(u'foo')
  >>> mytypes[u'bar'] = RelationType(u'bar')
  >>> mytypes[u'baz'] = RelationType(u'baz')

Note that we don't need to register the utility for IRelationTypes

  >>> component.provideUtility(mytypes, IMyTypes)

  >>> class MyRelationship(OneToOneRelationship):
  ...     @property
  ...     def relationtypes(self):
  ...         return component.getUtility(IMyTypes)

  >>> class MyRelationships(OneToOneRelationships):
  ...     @property
  ...     def relationtypes(self):
  ...         return component.getUtility(IMyTypes)

Check Relationship

  >>> myrelationship = MyRelationship(None, [u'foo'], None)
  >>> myrelationship.relations
  [<RelationType u'foo'>]

  >>> myrelationship = MyRelationship(None, [u'bar', u'baz'], None)
  >>> myrelationship.relations
  [<RelationType u'bar'>, <RelationType u'baz'>]

Check relationship container

  >>> item1 = Source(u'Fred')
  >>> item2 = Target(u'Barney')

  >>> myrelations = MyRelationships()
  >>> myrelationship = MyRelationship(item1, [u'foo'], item2)
  >>> myrelations.add(myrelationship)

Find sources

  >>> [o for o in myrelations.findSources(item2)]
  [<Source u'Fred'>]

  >>> [o for o in myrelations.findSources(item2, relation=u'foo')]
  [<Source u'Fred'>]

  >>> [o for o in myrelations.findSources(item2, relation=u'bar')]
  []

Find targets

  >>> [o for o in myrelations.findTargets(item1)]
  [<Target u'Barney'>]

  >>> [o for o in myrelations.findTargets(item1, relation=u'foo')]
  [<Target u'Barney'>]

  >>> [o for o in myrelations.findTargets(item1, relation=u'bar')]
  []

Find relationships

  >>> [o for o in myrelations.findSourceRelationships(item1)]
  [<MyRelationship ...>]

  >>> [o for o in myrelations.findSourceRelationships(item1, relation=u'foo')]
  [<MyRelationship ...>]

  >>> [o for o in myrelations.findSourceRelationships(item1, relation=u'bar')]
  []

  >>> [o for o in myrelations.findTargetRelationships(item2)]
  [<MyRelationship ...>]

  >>> [o for o in myrelations.findTargetRelationships(item2, relation=u'foo')]
  [<MyRelationship ...>]

  >>> [o for o in myrelations.findTargetRelationships(item2, relation=u'bar')]
  []

Configurator
------------

There is also a configurator implemented for site objects which
registers a IO2OStringTypeRelationships utility with a given name. The
name is optional.

  >>> from lovely.relation import configurator
  >>> util = configurator.SetUpO2OStringTypeRelationships(root)
  >>> util({'name':'myRelations'})
  >>> root.getSiteManager()['default']['o2oStringTypeRelationships_myRelations']
  <O2OStringTypeRelationships u'o2oStringTypeRelationships_myRelations'>

We can run it twice, so it does nothing.

  >>> util({'name':'myRelations'})

We also have a method for testing which is doing the setup.

  >>> from lovely.relation.testing import setUpPlugins
  >>> setUpPlugins()

An adapter has been registered.

  >>> from z3c.configurator.interfaces import IConfigurationPlugin
  >>> component.getAdapter(root,
  ...                      IConfigurationPlugin,
  ...                      name="lovely.relation.o2oStringTypeRelations")
  <lovely.relation.configurator.SetUpO2OStringTypeRelationships object at ...>

