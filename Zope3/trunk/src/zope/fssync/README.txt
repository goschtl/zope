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

* After update or commit for a single file, the other files and
  directories in the same directory are silently removed!!!!

TO DO
-----

* after committing an added or removed file, the flag doesn't get
  cleared in the entry

* unit tests for the fssync core functionality

* refactoring more of the fssync core functionality

* allow adding files of different types based on the file suffix or an
  explicit -t argument

* a 'status' command showing careful status

* more diff options:
  -2 diffs between local and remote
  -3 diffs between original and remote
  -N shows diffs for added/removed files as diffs with /dev/null
  more GNU diff options?  e.g. --ignore-space-change etc.
