Filesystem synchronization
--------------------------

This directory contains a utility (sync.py) and the modules it uses
that implement filesystem synchronization.  This is a little like CVS,
with the Data.fs service as the repository.  

Jim Fulton's original proposal explains the theory and background:

  http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/
  FileSystemSynchronizationProposal

The command line syntax of the utility is given in usage.py.

The implementation was originally written by Jim Fulton and ZeOmega's
deb_h.  It is now maintained by Guido van Rossum.
