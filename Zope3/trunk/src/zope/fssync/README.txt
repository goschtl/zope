Filesystem synchronization
==========================

For background and the original description by Jim Fulton, see:

  http://dev.zope.org/Zope3/FileSystemSynchronizationProposal

This version is based loosely on a prototype written by Jim Fulton and
Deb Hazarika.  It is now maintained by Fred Drake.

Possibly also relevant background:

  http://dev.zope.org/Zope3/ThroughTheWebSiteDevelopment

The "bundles" mentioned there are likely candidates for filesystem
synchronization.  (See section "Working with bundles" below.)


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

* An interesting possibility: you could couple your filesystem copy to
  a revision control system like CVS or Subversion, to have an
  auditable revision history of a site.  Typically, you'd do a cvs
  commit after each sync update and after each sync commit, after
  verifying that the state committed to Zope actually works.  It would
  be handy if files added to or removed from Zope are automatically
  added or removed from CVS.  The "binary" flag for CVS might be set
  automatically based on the Zope object type.

* Another possibility: export and import (a la Zope 2 export/import)
  should be easily implemented on top of this.  Export would be done
  with checkout; import could be a new "checkin" command.  (This is
  now implemented.)

* And last but not least, this will form the basis of bundles; see the
  ThroughTheWebSiteDevelopment reference above.


BUGS
----

* When committing an added file, you must commit the directory
  containing it; you can't commit the file itself, since the command
  tries to send the request to a view of the corresponding object,
  which doesn't exist yet.

* When doing an update, somehow the absolute pathnames of all files
  are reported rather than the nice relative names.


PLATFORM NOTES
--------------

* RedHat Linux 9:  Anthony Baxter reports that the tests can hang in a
  futex() system call.  It appears that the glibc version shipped with
  RedHat 9 (glibc-2.3.2-11) has some bug that causes this; updating to
  at least glibc-2.3.2-27.9 fixes the problem.


TO DO
-----

- Documentation for the zsync command line tool

- Explicit import/export facilities, similar to the functionality
  found in Zope 2

  * Should produce a single file (.zip or .tgz maybe)

- Improve some common data file formats (for example, simplify the
  Entries.xml file, possibly using ZConfig instead of XML, or at least
  something more speciallized than an XML pickle).

- Figure out how to write meaningful adapter tests.

- More adapters.  Should make sure that an XML Pickle will always work
  as a serialization, even if an adapter gets added.

- For objects serialized as XML pickles which are
  IAttributeAnnotatable and have an __annotations__ key in the pickled
  dictionary, separate the annotations from the dict so they appear in
  the @@Zope/Annotations/ tree.

- Implement bundle commands.

  * Need a way to turn site-management folders into bundles, and
    vice-versa; could be from command-line/zsync or more directly
    through the ZMI.

  * Once something is "marked" as a bundle, it should be read-only.

- Work out security details (before beta).

  * A commit unpickles user-provided data.  Unpickling is not a safe
    operation.  Possible solution: have an unpickler that finds globals
    in a secure way.  Use an import on a security proxy for sys.modules.

  * The adapters returned by the fs registry should optionally have a
    permission associated with them.  If you have an adapter that
    calls removeAllProxies or trustedRemoveSecurityProxy, the adapter
    should require a permission.

- In the sync application (nice-to-haves):

  * More diff options:
    -2 diffs between local and remote
    -3 diffs between original and remote
    -N shows diffs for added/removed files as diffs with /dev/null

  * Something akin to cvs -n update, which shows what update would do
    without actually doing it.

  * Make the commands more closely match Subversion, since the model
    is more similar.

  * Add support for HTTP proxies.

  * Implement diff using difflib.  (is this really needed?)

- Code maintenance:

  * Unit tests for the zsync utility.

  * Rewrite toFS() to use the Metadata class, and add unit tests.

  * More refactoring and cleanup of the zsync utility (the
    zope.fssync.main module)

  * Use camelCase for public method names.

- Refine the fssync adapter protocol or implementation to leverage the
  file-system representation (== FTP, WebDAV) protocol.

  * look in: zope.app.interface.file

- In common case where extra data are simple values, store extra data
  in the entries file to simplify representation and updates.  Maybe
  do something similar w/ annotations.

- Maybe leverage adaptable storage (APE) ideas to assure losslessness.


Working with bundles
--------------------

- Bundles aren't quite as easy to use as they are supposed to be as
  described in the ThroughTheWebSiteDevelopment Wiki page referenced
  above, but you can do some basic bundle-ish things.  All these need
  is a little better packaging.

- Permissions.  Everything described here requires the
  zope.ManageServices permission, which usually requires being logged
  in with the manager role.

- Bundle status.  There is not yet an explicit notion of "bundle-ness"
  for site management folders.  Any site management folder can be
  treated as a bundle.  Exception: the Bundle view works for the
  default folder but the form included in the view refuses to change
  it.  This is a safety measure: the bundle form can do a lot of
  damage, e.g. it can disable all services at once.  By convention, I
  propose that bundles have a folder name of the form
  <name>-<version>, where <version> is two or more decimal numbers
  separated by dots and <name> is unconstrained.

- Creating a bundle.  There is no specific command to create a
  bundle.  Instead, you create a new site management folder by going
  to the Contents view of the site (e.g. /++etc++site/@@contents.html)
  and clicking on "Add" in the actions menu.  A box will appear in
  which you should type the name + version of your bundle.  Then in
  that bundle you should create the things that you want to go into
  the bundle, e.g. modules, templates, services, utilities, etc.

- Creating a bundle from an existing folder.  If you have some
  existing work done in the default folder or another non-bundle
  folder, you can save your work to the filesystem using the zsync
  checkout command, and then check it in under a different name using
  the zsync checkin command.  Example; replace u:p with your manager
  username and password:

  $ zsync checkout http://u:p@localhost:8080/++etc++site/default
  <lots of output>
  All done.
  $ zsync checkin http://u:p@localhost:8080/++etc++site/bundle-1.0 default
  $

  Now go back to your web browser and check out the contents of
  /++etc++site/; a new folder bundle-1.0 should exist, containing a
  copy of the default folder.  You should delete unnecessary things;
  especially the standard service definitions are not needed.

- Exporting a bundle.  First deactivate the bundle by using the
  "Deactivate bundle" button on the Bundle tab (see below).  Then save
  the bundle to the filesystem using zsync checkout.  Finally tar or
  zip it up.  Make sure to include the @@Zope directory at the same
  level as the bundle directory in the archive.  Example:

  $ zsync checkout http://u:p@localhost:8080/++etc++site/bundle-1.0
  <lots of output>
  All done.
  $ tar tf - bundle-1.0 @@Zope | gzip >bundle-1.0.tgz
  $

  Now distribute the gzipped tar file via the web.

- Importing a bundle.  First extract the zip or tar file to the
  filesystem.  Then use zsync checkin command to add it to your Zope
  server.  Warning: the checkin command will happily overwrite an
  existing site management folder!

- Activating a bundle.  An imported bundle is completely inactive.
  Its configuration records (the objects in the bundle's
  RegistrationManager subfolder, and in RegistrationManager subfolders
  of subfolders of the bundle) are not registered with their
  respective services.  To activate the bundle, navigate your web
  browser to its contents and select the Bundle tab; it is probably
  the second tab from the left.  The Bundle tab displays two sections
  and a few buttons.

  - Section one of the Bundle tab shows the services needed by the
    bundle.  This list is created by inspection of the bundle's
    configuration records: for example, if there is a configuration
    record for a utility, the service needs the utility service.
    For each needed service, there are three possibilities:

    1) The service is already active in the site.  This is probably
       because it exists in the default folder or in a previously
       installed bundle.

    2) The service is not yet active in the site but the bundle
       provides a configuration for the service.

    3) No usable definition of the service can be found.  Note that a
       service active in a parent site cannot be used.  This is called
       an unfulfilled dependency.  This means that the bundle cannot
       be activated.  A helpful link to the "Add service" view of the
       default folder is provided, where you can create (and
       activate!) the service and then navigate back to the bundle;
       but you may also import the service as part of another bundle.

  - Section two of the Bundle tab shows, for each of the service types
    shown in section one, all configuration records in the bundle for
    that service type.  Initially, all configurations are in the
    "Unregistered" state.  At the bottom of the list you will find a
    button which will register all configurations, and activate the
    ones that aren't in conflict with pre-existing registrations.
    Conflicts are indicated in red and provide a link to the
    conflicting active configuration record, probably in another
    bundle.  The automatic resolution of conflicts in favor of a newer
    version of the same bundle, mentioned in the Wiki, is not yet
    implemented; by default, whenever there is a conflict the
    conflicting configuration record in the bundle is not activated.
    You can resolve conflicts yourself in favor of the new bundle by
    clicking the radio button labeled "Register and activate".  You
    can also leave a configuration record inactive by clicking the
    radio button "Register only".  When you are satisfied with the
    selections, click the "Activate bundle" button below the list to
    register and activate the bundle's configuration records; this
    performs the actions selected by the radio buttons.  If you later
    change your mind, you can always go back to the Bundle tab and
    change your selections.

  - At the very bottom of the page is a button labeled "Deactivate
    bundle".  This is used for uninstalling a bundle; it makes all
    configuration records contained in the bundle inactive and
    unregistered.  It is also used for exporting a bundle; before you
    export a bundle, you should deactivate it (see above).  In
    contrast to the description in the Wiki, deactivating a bundle
    does not reactivate any configuration records that were active
    before the bundle was activated, because the configuration
    registries don't record this information; it can't distinguish
    between previously active and previously registered.  A redesign
    of the registries would be necessary to accommodate this feature.

- To delete a deactivated bundle, go to the site manager's contents
  display (/++etc++site/@@contents.html), select the checkbox in front
  of the bundle name, and click the Delete button below the list.
  Deleting an active bundle usually doesn't work because of the
  dependencies between the configuration records and the configured
  objects in the bundle.
