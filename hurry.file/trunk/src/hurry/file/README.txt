hurry.file fields
=================

The file widget is built on top of the HurryFile object::

  >>> from hurry.file import HurryFile
  >>> file = HurryFile('foo.txt', 'mydata')
  >>> file.filename
  'foo.txt'
  >>> file.data
  'mydata'
  >>> f = file.file
  >>> f.read()
  'mydata'

We can also create HurryFile objects from file-like objects::

  >>> from StringIO import StringIO
  >>> from zope import component
  >>> from hurry.file.interfaces import IFileRetrieval
  >>> fileretrieval = component.getUtility(IFileRetrieval)
  >>> file = fileretrieval.createFile('bar.txt', StringIO('test data'))
  >>> file.filename
  'bar.txt'
  >>> file.data
  'test data'
  >>> f = file.file
  >>> f.read()
  'test data'

This does exactly the same, but may be easier to use::

  >>> from hurry.file import createHurryFile
  >>> file = createHurryFile('test2.txt', StringIO('another test file'))
  >>> file.filename
  'test2.txt'
 
The HurryFile object normally stores the file data using ZODB
persistence. Files can however also be stored by tramline.  If
tramline is installed in Apache, the Tramline takes care of generating
ids for files and storing the file on the filesystem directly. The ids
are then passed as file data to be stored in the ZODB.

Let's first enable tramline.

The tramline directory structure is a directory with two subdirectories,
one called 'repository' and the other called 'upload'::

  >>> import tempfile, os
  >>> dirpath = tempfile.mkdtemp()
  >>> repositorypath = os.path.join(dirpath, 'repository')
  >>> uploadpath = os.path.join(dirpath, 'upload')
  >>> os.mkdir(repositorypath)
  >>> os.mkdir(uploadpath)

We create a TramlineFileRetrieval object knowing about this directory,
and register it as a utility::

  >>> from hurry.file.file import TramlineFileRetrievalBase
  >>> class TramlineFileRetrieval(TramlineFileRetrievalBase):
  ...    def getTramlinePath(self):
  ...        return dirpath
  >>> retrieval = TramlineFileRetrieval()
  >>> component.provideUtility(retrieval, IFileRetrieval)

Now let's store a file the way tramline would during upload::

  >>> f = open(os.path.join(repositorypath, '1'), 'wb')
  >>> f.write('test data')
  >>> f.close()

The file with the data '1' will now be created::

  >>> file = HurryFile('foo.txt', '1')

The data is now '1'::

  >>> file.data
  '1'

Retrieving the file results in the real file::
  
  >>> f = file.file
  >>> f.read()
  'test data'

It should be possible to create Hurry File objects that are stored in
the directory structure directly::

  >>> file = retrieval.createFile('test.txt', StringIO('my test data'))
  >>> file.filename
  'test.txt'

We get an id for the data now::

  >>> file.data != 'my test data'
  True

And we can retrieve the file itself::

  >>> f = file.file
  >>> f.read()
  'my test data'

Now let's disable tramline in our utility::

  >>> class TramlineFileRetrieval(TramlineFileRetrievalBase):
  ...     def getTramlinePath(self):
  ...        return dirpath
  ...     def isTramlineEnabled(self):
  ...        return False
  >>> component.provideUtility(TramlineFileRetrieval(), IFileRetrieval)

We expect the same behavior as when tramline is not installed::

  >>> file = HurryFile('foo.txt', 'data')
  >>> f = file.file
  >>> f.read()
  'data'

Clean up::

  >>> import shutil
  >>> shutil.rmtree(dirpath)
