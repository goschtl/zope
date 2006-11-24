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
  ...     i =  api.getInterfacesFor(file(path, 'rb'))
  ...     print name
  ...     print i
  DS_Store
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IBinaryFile>])
  IMG_0504.JPG
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IJPGFile>])
  faces_gray.avi
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IAVIFile>])
  ftyp.mov
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IQuickTimeFile>])
  jumps.mov
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IQuickTimeFile>])
  logo.gif
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IGIFFile>])
  logo.gif.bz2
  set([<InterfaceClass z3c.filetype.interfaces.filetypes.IBZIP2File>])
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
  '...test.tar'
  >>> sorted(api.getInterfacesFor(f.name))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]


Applying filetype interfaces to objects via events
==================================================

There are event handlers which apply filetype interfaces to an
object. This object needs to implement ITypeableFile. So let us setup
the event handling.

  >>> from zope.component import eventtesting
  >>> eventtesting.setUp()

  >>> from z3c.filetype import interfaces
  >>> from zope import interface
  >>> class Foo(object):
  ...     interface.implements(interfaces.ITypeableFile)
  ...     def __init__(self, f):
  ...         self.data = f
  >>> foo = Foo(f)

There is also an event handler registered for IObjectCreatedEvent and
IObjectModified on  ITypeableFile. We register them here in the test.

  >>> from zope import component
  >>> component.provideHandler(api.handleCreated)
  >>> component.provideHandler(api.handleModified)

So we need to fire an IObjectCreatedEvent. Which is normally done by a
factory.

  >>> from zope.lifecycleevent import ObjectCreatedEvent
  >>> from zope.lifecycleevent import ObjectModifiedEvent
  >>> from zope.event import notify
  >>> eventtesting.clearEvents()
  >>> notify(ObjectCreatedEvent(foo))
  >>> sorted(eventtesting.getEvents())
  [<z3c.filetype.event.FileTypeModifiedEvent object at ...>,
   <zope.app.event.objectevent.ObjectCreatedEvent object at ...>]

The object now implements the according interface. This is achieved by
the evennthandler which calls applyInterfaces.

  >>> sorted((interface.directlyProvidedBy(foo)))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]

A second applyInteraces does nothing.

  >>> eventtesting.clearEvents()
  >>> api.applyInterfaces(foo)
  False
  >>> eventtesting.getEvents()
  []


If we change the object the interface changes too. We need to fire
an IObjectModifiedevent. Which is normally done by the implementation.

  >>> foo.data = file(os.path.join(testData,'test.flv'), 'rb')
  >>> eventtesting.clearEvents()
  >>> 
  >>> notify(ObjectModifiedEvent(foo))

Now we have two events, one we fired and one from our handler.

  >>> eventtesting.getEvents()
  [<zope.app.event.objectevent.ObjectModifiedEvent object at ...>,
   <z3c.filetype.event.FileTypeModifiedEvent object at ...>]

Now the file should implement another filetype.

  >>> sorted((interface.directlyProvidedBy(foo)))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IFLVFile>]

There is also an adapter from ITypedFile to IFileType, which can be
used to get the default content type for the interface.

  >>> from z3c.filetype import adapters
  >>> component.provideAdapter(adapters.TypedFileType)
  >>> ft = interfaces.IFileType(foo)
  >>> ft.contentType
  'video/x-flv'
  

Let us try an unknown file type, this should apply an IBinaryFile
interface.

  >>> foo.data = file(os.path.join(testData,'DS_Store'), 'rb')
  >>> notify(ObjectModifiedEvent(foo))
  >>> sorted((interface.directlyProvidedBy(foo)))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IBinaryFile>]  


  >>> foo.data = file(os.path.join(testData,'ftyp.mov'), 'rb')
  >>> notify(ObjectModifiedEvent(foo))
  >>> sorted((interface.directlyProvidedBy(foo)))
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IQuickTimeFile>]
  >>> interfaces.IFileType(foo).contentType
  'video/quicktime'

Size adapters
=============

There are adapters registered for ISized for IPNGFile, IJPEGFile and
IGIFFile.

  >>> from z3c.filetype import size
  >>> from zope.size.interfaces import ISized
  >>> component.provideAdapter(size.GIFFileSized)
  >>> component.provideAdapter(size.PNGFileSized)
  >>> component.provideAdapter(size.JPGFileSized)

  >>> foo.data = file(os.path.join(testData,'thumbnailImage_small.jpeg'), 'rb')
  >>> notify(ObjectModifiedEvent(foo))
  >>> ISized(foo).sizeForDisplay().mapping
  {'width': '120', 'height': '90', 'size': '3'}

  >>> foo.data = file(os.path.join(testData,'test.png'), 'rb')
  >>> notify(ObjectModifiedEvent(foo))
  >>> ISized(foo).sizeForDisplay().mapping
  {'width': '279', 'height': '19', 'size': '4'}

  >>> foo.data = file(os.path.join(testData,'logo.gif'), 'rb')
  >>> notify(ObjectModifiedEvent(foo))
  >>> ISized(foo).sizeForDisplay().mapping
  {'width': '201', 'height': '54', 'size': '2'}

  >>> foo.data = file(os.path.join(testData,'IMG_0504.JPG'), 'rb')
  >>> notify(ObjectModifiedEvent(foo))
  >>> ISized(foo).sizeForDisplay().mapping
  {'width': '1600', 'height': '1200', 'size': '499'}


