==================
Zope Release Tools
==================

This package provides some tools to manage Zope 3 releases. It extends the
scripts provided by ``zope.kgs`` with Zope-specifc scripts, such as updating
the Zope 3 source tree and uploading files to the download location.

Here is an examplatory controlled packages configuration file:

  >>> import tempfile
  >>> cfgFile = tempfile.mktemp('-cp.cfg')
  >>> open(cfgFile, 'w').write('''\
  ... [DEFAULT]
  ... tested = true
  ...
  ... [KGS]
  ... name = zope-dev
  ... version = 1.0.0
  ...
  ... [packageA]
  ... versions = 1.0.0
  ...            1.0.1
  ...
  ... [packageB]
  ... versions = 1.2.3
  ...
  ... [packageC]
  ... # Do not test this package.
  ... tested = false
  ... versions = 4.3.1
  ... ''')


Uploading Files
---------------

Once the generated files are tested and ready for upload, you can use the
upload script to upload the files to the KGS. Since we do not actually want to
upload files, we simply switch into dry-run mode:

  >>> from zope.release import upload
  >>> upload.DRY_RUN = True

Usually we only need to upload the controlled packages file, since site script
of the ``zope.kgs`` package will do the rest for us.

  >>> upload.main((cfgFile, 'download.zope.org:/zope-dev'))
  scp ...-cp.cfg download.zope.org:/zope-dev/...-cp.cfg


Updating the Zope 3 Tree
------------------------

Since we still want to create a Zope 3 source tree release, we need to be able
to update its externals using the information of the controlled packages
file. Since this script is clearly Zope3-specific, we need a new controlled
packages config file that contains actual packages:

  >>> import tempfile
  >>> zopeCfgFile = tempfile.mktemp('-cp.cfg')
  >>> open(zopeCfgFile, 'w').write('''\
  ... [DEFAULT]
  ... tested = true
  ...
  ... [KGS]
  ... name = zope
  ... version = dev
  ...
  ... [ZODB3]
  ... versions = 1.0.0
  ...
  ... [ZConfig]
  ... versions = 1.1.0
  ...
  ... [pytz]
  ... versions = 2007g
  ...
  ... [zope.interface]
  ... versions = 1.2.0
  ...
  ... [zope.app.container]
  ... versions = 1.3.0
  ... ''')

We also need to stub the command execution, since we do not have an actual Zope
3 tree checked out:

  >>> cmdOutput = {
  ...     'svn propget svn:externals Zope3/src': '''\
  ... docutils   path/to/docutils
  ... pytz       path/to/pytz
  ... twisted    path/to/twisted
  ... ZConfig    path/to/ZConfig
  ... ZODB       path/to/ZODB''',
  ...     'svn propget svn:externals Zope3/src/zope': '''\
  ... interface  path/to/zope/interface''',
  ...     'svn propget svn:externals Zope3/src/zope/app': '''\
  ... container  path/to/zope/app/container''',
  ... }

  >>> def do(cmd):
  ...     print cmd
  ...     print '-----'
  ...     return cmdOutput.get(cmd, '')

  >>> from zope.release import tree
  >>> tree.do = do

Let's now run the tree update:

  >>> tree.main((zopeCfgFile, 'Zope3'))
  svn propget svn:externals Zope3/src
  -----
  svn propset svn:externals
    "docutils svn://svn.zope.org/repos/main/docutils/tags/0.4.0/
     pytz svn://svn.zope.org/repos/main/pytz/tags/2007g/src/pytz
     twisted svn://svn.twistedmatrix.com/.../twisted-core-2.5.0/twisted
     ZConfig svn://svn.zope.org/repos/main/ZConfig/tags/1.1.0/ZConfig
     ZODB svn://svn.zope.org/repos/main/ZODB/tags/1.0.0/src/ZODB"
    Zope3/src
  -----
  svn propget svn:externals Zope3/src/zope
  -----
  svn propset svn:externals
    "interface svn://svn.zope.org/repos/main/zope.interface/tags/1.2.0/src/zope/interface" Zope3/src/zope
  -----
  svn propget svn:externals Zope3/src/zope/app
  -----
  svn propset svn:externals
    "container svn://svn.zope.org/repos/main/zope.app.container/tags/1.3.0/src/zope/app/container" Zope3/src/zope/app
  -----
