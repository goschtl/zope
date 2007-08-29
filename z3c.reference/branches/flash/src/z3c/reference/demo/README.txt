==================
 Demo application
==================

We test the references from our DemoFolder and DemoImage.

  >>> from z3c.reference.demo.app import (DemoFolder,
  ...                                     DemoImage)
  >>> from z3c.reference.reference import ViewReference

Let's create some DemoFolders and let them reference themselves.

  >>> f1 = DemoFolder()
  >>> f2 = DemoFolder()
  >>> f3 = DemoFolder()
  >>> r1 = ViewReference(target=f2)
  >>> r2 = ViewReference(target=f3)
  >>> f1.assets = [r1, r2]

Check reference target and parent.

  >>> len(f1.assets)
  2
  >>> f1.assets[0].target is f2
  True
  >>> f2.viewReferences[0].__parent__ is f1
  True

Add another reference to demo folder 3.

  >>> r3 = ViewReference(target=f3)
  >>> f2.assets = [r3]

Check size of backreferences and on valid parents.

  >>> len(f3.viewReferences)
  2
  >>> f3.viewReferences[0].__parent__ is f1
  True
  >>> f3.viewReferences[1].__parent__ is f2
  True

Now we create a DemoImage and reference a DemoFolder with it.

  >>> i1 = DemoImage()
  >>> r4 = ViewReference(target=i1)
  >>> f3.assets = [r4]

Check reference target and parent.

  >>> f3.assets[0].target is i1
  True
  >>> i1.viewReferences[0].__parent__ is f3
  True

Add another reference to i1.

  >>> r5 = ViewReference(target=i1)
  >>> f2.assets = [r5]
  >>> f2.assets[0].target is i1
  True
  >>> i1.viewReferences[1].__parent__ is f2
  True
  >>> len(i1.viewReferences)
  2

Sets the previewImage for f1.

  >>> i2 = DemoImage()
  >>> r6 = ViewReference(target=i2)
  >>> f1.previewImage = r6

Check reference target and parent

  >>> f1.previewImage.target is i2
  True
  >>> i2.viewReferences[0].__parent__ is f1
  True


