Filesystem synchronization
==========================

For background and the original description by Jim Fulton, see:

  http://dev.zope.org/Zope3/FileSystemSynchronizationProposal

This version is based loosely on a prototype written by Jim Fulton and
Deb Hazarika.  It is now maintained by Guido van Rossum.


User stories
------------

* A user with site development privileges plans to go offline for a
  weekend and wants to work on (part of) the site on his laptop during
  that time.  On Friday, before going offline, he checks out a subtree
  of the site to his laptop's disk.  This maps folders to directories
  and other objects to files.  Metadata is stored in a subdirectory
  named @@Zope, some of it as XML.  Over the weekend he edits the
  files and perhaps the metadata on his laptop.  On Monday, once
  online again, he commits his work back to the site.

* It is possible that someone else might have made changes to the site
  that conflict with the work done offline.  The commit operation
  should fail in this case without making any changes.  Our user
  should then invoke an update command that merges the site's changes
  into his local work area.  If there are any merge conflicts, he
  should then resolve these manually.  Once conflicts are resolved, he
  can commit his changes successfully, assuming there are no
  additional changes made to the site in the mean time; otherwise, the
  commit will fail again and the cycle starts over.

* Like CVS, after doing a successful commit, you can continue to work
  and do another commit later.

* There should be commands to show the differences in the local copy,
  and to show the status of each file or directory.

* Merging changes should deal with simultaneous changes in the same
  file, at least for text files; what CVS does is pretty reasonable
  (this seems to be based on the diff3 command).

* Update and commit should handle addition and removal of files and
  directories.  For local additions and removals, an explicit command
  must be given to confirm these, to avoid committing files that were
  accidentally created or lost.

* Commands that are reasonable to do offline (e.g. add, remove,
  status, and the simplest form of diff) must be performed entirely
  offline.


BUGS
----

* When committing an added file, you must commit the directory
  containing it; you can't commit the file itself, since the command
  tries to send the request to a view of the corresponding object,
  which doesn't exist yet.

* When dealing with additions or removals, sometimes multiple updates
  are required to get the Extra stuff to be updated.

* Removing a directory tree doesn't work intuitively; if you "rm -r" a
  subtree and then "sync remove" it, a following "sync commit" causes
  a server-side exception.  It should just work.  (As a work-around,
  you can remove individual files and commit those removals first,
  then remove the directory last.)

* When committing something creates additional stuff (for example,
  committing an added site folder creates a RegistrationManager inside
  the site folder), the commit operation doesn't send the created
  stuff back necessarily.  (As a work-around, a subsequent update gets
  them.)

* Removing an object with annotations doesn't always remove the
  @@Zope/Annotations/<name>/ directory.  Probably the same for Extra.

* When doing an update, somehow the absolute pathnames of all files
  are reported rather than the nice relative names.


TO DO
-----

- On the server side:

  * Should be able to add various standard object types based on
    filename extension.  (This now works for extensions .pt and .dtml;
    for other extensions, either an image or a plain file is created
    based on the extension and the contents.  Is this good enough?)

  * When committing a change, shouldn't the mtime in the DC metadata
    be updated?

- In the sync application:

  * Implement diff using difflib.

  * More diff options:
    -2 diffs between local and remote
    -3 diffs between original and remote
    -N shows diffs for added/removed files as diffs with /dev/null

  * More GNU diff options?  e.g. --ignore-space-change etc.

  * Something akin to cvs -n update, which shows what update would do
    without actually doing it.

- Code maintenance:

  * Unit tests for the fssync core functionality.

  * More refactoring and cleanup of the fssync core functionality.

  * Use camelCase for method names.


TO DO LATER
-----------

* Work out security details.

* A commit unpickles user-provided data.  Unpickling is not a safe
  operation.  Possible solution: have an unpickler that finds globals
  in a secure way.  Use an import on a security proxy for sys.modules.

* The adapters returned by the fs registry should optionally have
  a permission associated with them.  If you have an adapter that
  calls removeAllProxies, the adapter should require a permission.

* Refine the fssync adapter protocol or implementation to leverage the
  file-system representation (== FTP, WebDAV) protocol.

* In common case where extra data are simple values, store extra data
  in the entries file to simplify representation and updates.  Maybe
  do something similar w annotations.

* Maybe do some more xmlpickle refinement with an eye toward
  improving the usability of simple dictionary pickles.

* Maybe leverage adaptable storage ideas to assure losslessness.

* Export and import as a special case.

* Improve some common data file formats (e.g. simplify entries file).

* Commit to multiple Zope instances?

* Diff/merge multiple working sets (a la bitkeeper)?
