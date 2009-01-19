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
  ...     i =  api.getInterfacesFor(file(path, 'rb'), filename=name)
  ...     print name
  ...     print sorted(i)
  DS_Store
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IBinaryFile>]
  IMG_0504.JPG
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IJPGFile>]
  excel.xls
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IMSWordFile>]
  faces_gray.avi
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IAVIFile>]
  ftyp.mov
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IQuickTimeFile>]
  ipod.mp4
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IMP4File>]
  jumps.mov
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IQuickTimeFile>]
  logo.gif
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IGIFFile>]
  logo.gif.bz2
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IBZIP2File>]
  mpeglayer3.mp3
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IAudioMPEGFile>]
  noface.bmp
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IBMPFile>]
  portable.pdf
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IPDFFile>]
  powerpoingt.ppt
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IMSWordFile>]
  test.flv
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IFLVFile>]
  test.gnutar
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]
  test.html
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IHTMLFile>]
  test.png
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IPNGFile>]
  test.tar
  [<InterfaceClass z3c.filetype.interfaces.filetypes.ITARFile>]
  test.tgz
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IGZIPFile>]
  test.txt.gz
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IGZIPFile>]
  test2.html
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IHTMLFile>]
  test2.thml
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IHTMLFile>]
  thumbnailImage_small.jpeg
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IJPGFile>]
  word.doc
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IMSWordFile>]

It is not possible to reliably detect Microsoft Office files from file data.
The only way right now is to use the filename.

  >>> for name in fileNames:
  ...     if name==".svn": continue
  ...     i =  api.getInterfacesFor(filename=name)
  ...     print name
  ...     print sorted(i)
  DS_Store
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IBinaryFile>]
  ...
  excel.xls
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IMSExcelFile>]
  ...
  powerpoingt.ppt
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IMSPowerpointFile>]
  ...
  word.doc
  [<InterfaceClass z3c.filetype.interfaces.filetypes.IMSWordFile>]


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


IFileType adapters
==================

There is also an adapter from ITypedFile to IFileType, which can be
used to get the default content type for the interface.

  >>> from z3c.filetype import adapters
  >>> component.provideAdapter(adapters.TypedFileType)
  >>> for name in fileNames:
  ...     if name==".svn": continue
  ...     path = os.path.join(testData, name)
  ...     i =  Foo(file(path, 'rb'))
  ...     notify(ObjectModifiedEvent(i))
  ...     print name + " --> " + interfaces.IFileType(i).contentType
  DS_Store --> application/octet-stream
  IMG_0504.JPG --> image/jpeg
  excel.xls --> application/msword
  faces_gray.avi --> video/x-msvideo
  ftyp.mov --> video/quicktime
  ipod.mp4 --> video/mp4
  jumps.mov --> video/quicktime
  logo.gif --> image/gif
  logo.gif.bz2 --> application/x-bzip2
  mpeglayer3.mp3 --> audio/mpeg
  noface.bmp --> image/bmp
  portable.pdf --> application/pdf
  powerpoingt.ppt --> application/msword
  test.flv --> video/x-flv
  test.gnutar --> application/x-tar
  test.html --> text/html
  test.png --> image/png
  test.tar --> application/x-tar
  test.tgz --> application/x-gzip
  test.txt.gz --> application/x-gzip
  test2.html --> text/html
  test2.thml --> text/html
  thumbnailImage_small.jpeg --> image/jpeg
  word.doc --> application/msword



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


