==================
 Demo application
==================

We test the references from our DemoFolder and DemoImage.

  >>> from z3c.reference.demo.app import (DemoFolder,
  ...                                     DemoImage)

Let's create some DemoFolders and let them reference themselves.

  >>> f1 = DemoFolder()
  >>> f2 = DemoFolder()
  >>> f3 = DemoFolder()
  >>> r1 = DemoFolder.assets.new(f2)
  >>> r2 = DemoFolder.assets.new(f3)
  >>> f1.assets = [r1, r2]

Check reference target and parent.

  >>> len(f1.assets)
  2
  >>> f1.assets[0].target is f2
  True
  >>> from lovely.relation.property import PropertyRelationManager
  >>> manager = PropertyRelationManager(f2, 'viewReferences')
  >>> refs = list(manager.getRelations('folder.assets'))
  >>> refs[0].source is f1
  True

Add another reference to demo folder 3.

  >>> r3 = DemoFolder.assets.new(f3)
  >>> f2.assets = [r3]

Check size of backreferences and on valid sources.

  >>> manager = PropertyRelationManager(f3, 'viewReferences')
  >>> refs = list(manager.getRelations('folder.assets'))
  >>> len(refs)
  2
  >>> refs[0].source is f1
  True
  >>> refs[1].source is f2
  True

Now we create a DemoImage and reference a DemoFolder with it.

  >>> i1 = DemoImage()
  >>> r4 = DemoFolder.assets.new(i1)
  >>> f3.assets = [r4]

Check reference target and parent.

  >>> f3.assets[0].target is i1
  True
  >>> manager = PropertyRelationManager(i1, 'viewReferences')
  >>> refs = list(manager.getRelations('folder.assets'))
  >>> refs[0].source is f3
  True

Add another reference to i1.

  >>> r5 = DemoFolder.assets.new(i1)
  >>> f2.assets = [r5]
  >>> f2.assets[0].target is i1
  True
  >>> manager = PropertyRelationManager(i1, 'viewReferences')
  >>> refs = list(manager.getRelations('folder.assets'))
  >>> refs[1].source is f2
  True
  >>> len(refs)
  2

We add i1 as previewImage to f2.

  >>> rr = DemoFolder.previewImage.new(i1)
  >>> f2.previewImage = rr
  >>> refs = list(manager.getRelations('folder.assets'))
  >>> len(refs)
  2

Now we have a backref from 'folder.previewImage'.

  >>> refs = list(manager.getRelations('folder.previewImage'))
  >>> len(refs)
  1
  >>> refs = list(manager.getAllRelations())
  >>> len(refs)
  3

Sets the previewImage for f1.

  >>> i2 = DemoImage()
  >>> r6 = DemoFolder.previewImage.new(i2)
  >>> f1.previewImage = r6

Check reference target and parent

  >>> f1.previewImage.target is i2
  True
  >>> manager = PropertyRelationManager(i2, 'viewReferences')
  >>> refs = list(manager.getRelations('folder.previewImage'))
  >>> refs[0].source is f1
  True

Settings
========

