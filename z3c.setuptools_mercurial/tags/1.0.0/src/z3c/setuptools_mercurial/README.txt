===========================================
Mercurial File Finder Plugin for Setuptools
===========================================

This package provides a simple, command-based file finder plugin for
setuptools. Once installed, one can create distributions using a pacakge that
has been checked out with Mercurial.

So let's create a workspace:

  >>> import tempfile
  >>> ws = tempfile.mkdtemp()

Since the workspace is not a mercurial repository, the finder returns an empty
list and leaves an error message in the logs:

  >>> from z3c.setuptools_mercurial import finder

  >>> finder.find_files(ws)
  abort: There is no Mercurial repository here (.hg not found)! (code 255)
  <BLANKLINE>
  []

Also, if the directory does not exist, we get an error message, but an empty
result set:

  >>> finder.find_files('/foo')
  [Errno 2] No such file or directory: '/foo'
  []

Let's now create a new repository:

  >>> import os
  >>> repos = os.path.join(ws, 'test')
  >>> cmd('hg init ' + repos)

The finder still fails with error code 1, since no file is yet added in the
repository:

  >>> finder.find_files(repos)
  (code 1)
  []

Let's now add soem directories and files and the finder should be happy.

  >>> cmd('touch ' + os.path.join(repos, 'data.txt'))
  >>> cmd('hg add ' + os.path.join(repos, 'data.txt'))

  >>> cmd('mkdir ' + os.path.join(repos, 'dir1'))
  >>> cmd('touch ' + os.path.join(repos, 'dir1', 'data1.txt'))
  >>> cmd('hg add ' + os.path.join(repos, 'dir1', 'data1.txt'))

  >>> cmd('mkdir ' + os.path.join(repos, 'dir1', 'dir11'))
  >>> cmd('touch ' + os.path.join(repos, 'dir1', 'dir11', 'data1.txt'))
  >>> cmd('hg add ' + os.path.join(repos, 'dir1', 'dir11', 'data1.txt'))

  >>> finder.find_files(repos)
  ['./data.txt',
   './dir1/data1.txt',
   './dir1/dir11/data1.txt']

Note that the result of the finder is always a list of relative locations
based on the input directory.
