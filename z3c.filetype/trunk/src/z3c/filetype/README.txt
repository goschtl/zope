================
Filetype Package
================

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
