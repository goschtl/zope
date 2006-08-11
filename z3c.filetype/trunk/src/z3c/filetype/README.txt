================
Filetype Package
================

:ATTENTION: This package is not ready yet! see TODO.txt

This package provides a way to get interfaces that are provided based
on their content, filename or mime-type.

  >>> from z3c.filetype import api

We take some files for demonstration from the testdata directory.

  >>> import os
  >>> testData = os.path.join(os.path.dirname(api.__file__),'testdata')

  >>> fileNames = sorted(os.listdir(testData))

  >>> for name in fileNames:
  ...     if name==".svn": continue
  ...     path = os.path.join(testData, name)
  ...     i =  api.getInterfacesFor(file(path))
  ...     print name
  ...     print i
  DS_Store
  set([])
  jumps.mov
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IVideoFile>])
  logo.gif
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IGIFFile>])
  test.flv
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IFLVFile>])
  test.gnutar
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>])
  test.html
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IHTMLFile>])
  test.png
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IPNGFile>])
  test.tar
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>])
  test.tgz
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IGZIPFile>])
  test.txt.gz
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IGZIPFile>])
  test2.html
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IHTMLFile>])
  test2.thml
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IHTMLFile>])
  thumbnailImage_small.jpeg
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IJPGFile>])

The filename is only used if no interface is found, because we should
not trust the filename in most cases.

  >>> f = open(os.path.join(testData, 'test.tar'))
  >>> sorted(api.getInterfacesFor(f))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]

  >>> sorted(api.getInterfacesFor(filename="x.png"))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IPNGFile>]

  >>> sorted(api.getInterfacesFor(f, filename="x.png"))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]


If a mimeType is given then the interfaces derived from it is added to
the result, regardless if the content of the file tells something
different.

  >>> sorted(api.getInterfacesFor(f, mimeType="text/plain"))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>,
   <InterfaceClass z3c.filetype.interfaces.filetypes.ITextFile>]

You can also provide a path instead of a stream.

  >>> f.name
  '/.../z3c/filetype/testdata/test.tar'
  >>> sorted(api.getInterfacesFor(f.name))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]


There is also a convinience function which applies filetype interfaces
to an object. This object needs to implement ITypeableFile. This also
fires events, so let us setup the event handling.

  >>> from zope.component import eventtesting
  >>> eventtesting.setUp()

  >>> from z3c.filetype import interfaces
  >>> from zope import interface
  >>> class Foo(object):
  ...     interface.implements(interfaces.ITypeableFile)
  ...     def __init__(self, f):
  ...         self.data = f
  >>> foo = Foo(f)

The applInterfaces method returns a boolean if changes occured.

  >>> api.applyInterfaces(foo)
  True

And an event should be have been fired.

  >>> eventtesting.getEvents()
  [<z3c.filetype.event.FileTypeModifiedEvent object at ...>]

A second applyInteraces does nothing.

  >>> eventtesting.clearEvents()
  >>> api.applyInterfaces(foo)
  False
  >>> eventtesting.getEvents()
  []

Now the object should implement the right interface according to the
ata contained.

  >>> sorted((interface.directlyProvidedBy(foo)))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]

If we change the object the interface changes too.

  >>> foo.data = file(os.path.join(testData,'test.flv'))
  >>> api.applyInterfaces(foo)
  True
  >>> sorted((interface.directlyProvidedBy(foo)))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IFLVFile>]


There is also an event handler registered on IObjectModified for
ITypeableFile. We register it here in the test.

  >>> from z3c.filetype.event import handleModified
  >>> from zope import component
  >>> component.provideHandler(handleModified)
  >>> foo.data = file(os.path.join(testData,'test.html'))

So we need to fire an IObjectModifiedevent. Which is normally done by
the implementation.

  >>> from zope.lifecycleevent import ObjectModifiedEvent
  >>> from zope.event import notify
  >>> eventtesting.clearEvents()
  >>> notify(ObjectModifiedEvent(foo))

Now we have two events, one we fired and one from our handler.

  >>> eventtesting.getEvents()
  [<zope.app.event.objectevent.ObjectModifiedEvent object at ...>,
   <z3c.filetype.event.FileTypeModifiedEvent object at ...>]
  
Now the file should implement another filetype.

  >>> sorted((interface.directlyProvidedBy(foo)))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IHTMLFile>]


