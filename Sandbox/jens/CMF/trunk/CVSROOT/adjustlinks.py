#!/usr/local/bin/python2.1

"""Adjust symlinks in the repository according to the repolinks recipe file.

The repolinks file is found in the CVSROOT of the repository, along with this
script.

The links asserted by repolinks are compared with existing links in the
filesystem, and links are added and deleted as necessary.  See
LinkManager.assert_map() for specifics.

Errors - illegal or invalid paths, collisions, etc - are reported to
stderr."""

# Name of the recipe file - to be found in same directory as the script:
RECIPE_NAME = 'repolinks'
RESULTS_TO = 'klm@digicool.com'
QUIET = 0

import sys, os, stat
import string
SCRIPT_DIR = os.path.abspath(os.path.split(sys.argv[0])[0])
# Assume the repository root dir contains the CVSROOT script dir.
REPO_ROOT = os.path.split(SCRIPT_DIR)[0]
RECIPE_PATH = os.path.join(SCRIPT_DIR, RECIPE_NAME)

EMPTY_DIR = REPO_ROOT + "/CVSROOT/Emptydir"

def main(argv=None):
    lm = LinkManager()
    lm.assess_existing_links()
    lm.assert_map()

class LinkManager:
    """Maintain and implement repository symlink maps."""

    def __init__(self):
        """Assemble data structures."""
        # [(from, to, lineno), ...]
        self._recipe_lines = self.get_recipe_lines()
        # {actual_path: actual_target}
        self._fslinks = {}

    def assert_map(self,
                   isdir=os.path.isdir, isfile=os.path.isfile,
                   islink=os.path.islink, exists=os.path.exists,
                   abspath=os.path.abspath, split=os.path.split,
                   readlink=os.readlink, unlink=os.unlink, pjoin=os.path.join,
                   symlink=os.symlink, lstat=os.lstat, ST_INO=stat.ST_INO):
        """Impose the links specified by the recipe, removing preexisting
        links that are not specified in the map.  Specifically:

          - Add prescribed links that are absent, when there's no non-link
            file in the way.

          - Adjust already-existing links that don't point to the prescribed
            place - so we can use the file to redirect existing links.

          - Remove links that are not prescribed.

          - Do nothing for links that already exist as prescribed.

          - Warn about prescribed links that point nowhere.

          - Warn about prescribed links that cannot be created because the
            indicated containing dir does not exist.

          - Reiterate attempts until all are done, or no more progress is
            being made - so it's not a problem for links to be dependent on
            others in order to be situated.

          - Delete prescribed links that point outside the repository.

          - Produce output about all the actions."""

        link2inode = self._fslinks
        inode2link = {}
        for k, v in link2inode.items(): inode2link[v] = k

        # Confirm or create the prescribed links:

        pending = self._recipe_lines
        # Collect accounted-for links inodes, to prevent deletion in cleanup:
        done = []
        retargeted = []
        resolvedsome = 1

        # Since links can depend on eachother, we repeatedly loop as long
        # as stuff is pending and we're making progress:
        while resolvedsome and pending:

            resolvedsome = 0
            doing = pending
            pending = []
            for i in doing:
                link, target, lineno = i

                # Is it already there, as a link?
                if islink(link):
                    resolvedsome = 1
                    oldtarget = readlink(link)
                    # Is the existing one pointing at the right place?
                    if oldtarget != target:
                        info("Retargeting existing link %s\n"
                             "  => %s (was %s)",
                             link, target, oldtarget)
                        retargeted.append(lstat(link)[ST_INO])
                        unlink(link)
                        symlink(target, link)
                    done.append((link, target, lstat(link)[ST_INO]))

                # Is there a non-link in the way?
                elif exists(link):
                    resolvedsome = 1
                    warn("%s line %d: link blocked by non-link %s",
                         RECIPE_NAME, lineno, link)

                # Is the directory containing it there, to allow creating it?
                elif isdir(split(link)[0]):
                    info("Creating link:\n %s => %s", link, target)
                    symlink(target, link)
                    resolvedsome = 1
                    done.append((link, target, lstat(link)[ST_INO]))

                # Try again next time, if we're making progress - the
                # directory may eventually be established by another link:
                else:
                    pending.append(i)

        # Warn about infeasible links:
        for link, target, lineno in pending:
            warn("%s line %d: failed to place link %s",
                 RECIPE_NAME, lineno, link)

        # Cleanup:
        # - Remove any links that point outside the repository hierarchy
        # - Warn about links that don't point anywhere valid
        # - Remove obsolete links

        rootlen = len(REPO_ROOT)
        for link, target, inode in done:
            
            # Remove links that point outside the repository hierarchy:
            if abspath(pjoin(link, target))[:rootlen] != REPO_ROOT:
                warn("Removing illegal link to outside repository:\n"
                     "  %s => %s",
                     link, target)
                unlink(link)

            elif not exists(link):
                warn("Orphaned link - points at nothing:\n %s => %s",
                     link, readlink(link))

            # Cull accounted-for inode2link links, preparing for next step.
            if inode2link.has_key(inode):
               del inode2link[inode]

        # Most links still registered in inode2link are obsolete - remove them:
        for inode, link in inode2link.items():
            if inode not in retargeted:
                info("Removing obsolete link %s", link)
                unlink(link)

    def get_recipe_lines(self,
                         strip=string.strip, split=string.split,
                         pjoin=os.path.join, abspath=os.path.abspath,
                         isabs=os.path.isabs):
        """Return massaged list of recipe lines, as tuples:
        (from, to, lineno).  We omit non-recipe lines, and warn about
        malformed ones.

        See comments at repolinks file top for format."""
        lines = open(RECIPE_PATH).readlines()
        lineno = 0
        got = []
        for i in lines:
            lineno = lineno + 1
            i = strip(i)
            if not i or i[0] == '#':
                continue
            fields = split(i)
            if len(fields) > 2:
                warn("Skipping bad line %d - %d fields, should not exceed 2",
                     lineno, len(fields))
                continue
            elif len(fields) == 1:
                # Empty target means point to EMPTY_DIR - place holder for
                # removed dirs.
                link, target = fields[0], EMPTY_DIR
            else:
                link, target = fields
                if isabs(target):
                    target = REPO_ROOT + target
            delim = (not isabs(link) and os.sep) or ''
            link =  REPO_ROOT + delim + link
            got.append((link, target, lineno))
        # Warn about dups:
        links = {}
        for link, target, lineno in got:
            if links.has_key(link):
                warn("Duplicate link encountered on line %d (last on %d):\n"
                     "  %s", lineno, links[link], link)
            links[link] = lineno
        return got

    def assess_existing_links(self, readlink=os.readlink, lstat=os.lstat,
                              ST_INO=stat.ST_INO):
        """Walk the repository from the root, collecting existing links."""

        m = {}
        for i in find_fs_links(REPO_ROOT):
            m[i] = lstat(i)[ST_INO]
        self._fslinks = m
        return m

    def all_containers(self, path,
                       exists=os.path.exists, ST_INO=stat.ST_INO):
        """Given a repo-relative path, return *all* the repository paths that
        contain it - direct containers *and* directories that container it by
        virtue of symlinks in the repolinks map.

        This is used in postcommit_actions to identify all the
        checkin-notification subscriber entries that qualify for a particular
        file, not just the containers obvious from the checkin path.

        We expect a path relative to the repository root, and return paths
        relative to the repository root."""
        # We get the inodes of all the directories on the actual (physical)
        # path, and identify all those links whose targets are one of those
        # directories.

        got = {path: 1}

        if path[:len(os.sep)] == os.sep:
            # Strip the leading '/'
            path = path[len(os.sep):]
        path = os.path.join(REPO_ROOT, path)

        actual_path, element_inodes = path_element_inodes(path)
        if element_inodes:
            # Include actual path (relative to actual repo root).
            got[actual_path[len(ACTUAL_REPO_ROOT())+len(os.sep):]] = 1
            for link, target, lineno in self._recipe_lines:
                if (exists(target)
                    and (os.stat(target)[ST_INO] in element_inodes)):
                    # (Strip the REPO_ROOT prefix.)
                    got[link[len(REPO_ROOT)+len(os.sep):]] = 1

        return got.keys()

def path_element_inodes(path, split=os.path.split,
                        stat=os.stat, ST_INO=stat.ST_INO):
    """Return actual path relative to repository, and root inodes of directory
    elements leading to path's physical location.
    We return the empty list if path doesn't actually exist."""

    actual_path = None
    got = []
    if (os.path.exists(path) or os.path.exists(split(path)[0])):
        here = actual_path = actual_dir(path)
        while here and (here != '/'):
            got.insert(0, stat(here)[ST_INO])
            here = split(here)[0]
    return (actual_path, got)

def find_fs_links(dir,
                  join=os.path.join,
                  isdir=os.path.isdir, islink=os.path.islink):
    """Return a breadth-first list of paths of symlinks within dir."""
    got = []
    dirs = []

    for f in os.listdir(dir):
        p = join(dir, f)
        if islink(p): got.append(p)
        elif isdir(p): dirs.append(p)

    for d in dirs:
        got.extend(find_fs_links(d))

    return got

def actual_dir(path):
    """Return the real directory, as reported by os.getcwd from inside the dir.

    If the arg is not a directory, try with the final path element stripped."""
    origdir = os.getcwd()
    try:
        if os.path.isdir(path):
            os.chdir(path)
        else:
            os.chdir(os.path.split(path)[0])
        return os.getcwd()

    finally:
        os.chdir(origdir)

_ACTUAL_REPO_ROOT = None
def ACTUAL_REPO_ROOT():
    global _ACTUAL_REPO_ROOT
    if _ACTUAL_REPO_ROOT is None:
        _ACTUAL_REPO_ROOT = actual_dir(REPO_ROOT)
    return _ACTUAL_REPO_ROOT

def info(*args):
    if not QUIET:
        apply(warn, args, {'status': "-- Info"})

def warn(*args, **kw):
    status = kw.get('status', "** Warning")
    print "%s: %s" % (status, args[0] % args[1:])

if __name__ == "__main__":
    print ("  === %s run ===\n  ...on commit of %s...\n"
           % (sys.argv[0], RECIPE_PATH))
    main(sys.argv)
    print "-- Done."
