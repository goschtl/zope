import grok

import py
from datetime import datetime

from z3c.vcsync.interfaces import ICheckout

SVN_ERRORS = [("svn: Failed to add file '",
               "': object of the same name already exists\n"),
              ("svn: Failed to add file '",
               "': object of the same name is already scheduled for addition")]

class SvnCheckout(object):
    """A checkout for SVN.

    It is assumed to be initialized with py.path.svnwc
    """
    grok.implements(ICheckout)
    
    def __init__(self, path):
        self.path = path
        self._files = set()
        self._removed = set()
        self._revision_nr = None
        self._updated_revision_nr = None
    
    def _repository_url(self):
        prefix = 'Repository Root: '
        lines = self.path._svn('info').splitlines()
        for line in lines:
            if line.startswith(prefix):
                break
        return line[len(prefix):].strip()

    def _checkout_path(self):
        """Path to checkout from SVN's perspective.
        """
        checkout_url = self.path.info().url
        repos_url = self._repository_url()
        return checkout_url[len(repos_url):]
    
    def up(self):
        # these need to be initialized here and will be used
        # here and in resolve
        self._found_files = set()
        while True:
            try:
                self.path.update()
            except py.process.cmdexec.Error, e:
                # if an added file is in the way of doing an update...
                err = e.err
                for start, end in SVN_ERRORS:
                    if err.startswith(start) and err.endswith(end):
                        err_path = err[len(start):-len(end)]
                        path = self._svn_path(py.path.local(err_path))
                        self._found(path, path.read())
                        path.remove()
                        break
                    # loop again, try another SVN update
                else:
                    raise
            else:
                # we're done
                break

        self._updated_revision_nr = None
        
    def resolve(self):
        self._resolve_helper(self.path)

    def commit(self, message):
        revision_nr = self.path.commit(message)
        if revision_nr is None:
            revision_nr = int(self.path.status().rev)
        self._revision_nr = revision_nr
        
    def files(self, revision_nr):
        self._update_files(revision_nr)
        return list(self._files)
    
    def removed(self, revision_nr):
        self._update_files(revision_nr)
        return list(self._removed)

    def revision_nr(self):
        return self._revision_nr

    def _found(self, path, content):
        """Store conflicting/lost content in found directory.

        path - the path in the original tree. This is translated to
               a found path with the same structure.
        content - the file content
        """
        save_path = self._found_path(path)
        save_path.ensure()
        save_path.write(content)
        self._add_parts(save_path)

    def _found_container(self, path):
        """Store conflicting/lost container in found directory.

        path - the path in the original tree. This is translated to
               a found path with the same structure.
        """
        save_path = self._found_path(path)
        py.path.local(path.strpath).copy(save_path)
        save_path.add()
        self._add_parts(save_path)
        for new_path in save_path.visit():
            new_path.add()
            self._found_files.add(new_path)

    def _add_parts(self, path):
        """Given a path, add containing folders if necessary to found files.
        """
        self._found_files.add(path)
        for part in path.parts()[:-1]:
            if self._is_new(part):
                self._found_files.add(part)
        
    def _is_new(self, path):
        """Determine whether path is new to SVN.
        """
        # if we're above the path in the tree, we're not new
        if path <= self.path:
            return False
        return path in path.status().added
    
    def _update_files(self, revision_nr):
        """Go through svn log and update self._files and self._removed.
        """
        new_revision_nr = int(self.path.status().rev)
        if self._updated_revision_nr == new_revision_nr:
            return
        if new_revision_nr > revision_nr:
            # we don't want logs to include the entry for revision_nr itself
            # so we add + 1 to it
            logs = self.path.log(revision_nr + 1, new_revision_nr,
                                 verbose=True)
        else:
            # the log function always seem to return at least one log
            # entry (the latest one). This way we skip that check if not
            # needed
            logs = []
        checkout_path = self._checkout_path()
        files, removed = self._info_from_logs(logs, checkout_path)
        self._files = files.union(self._found_files)
        self._removed = removed
        self._updated_revision_nr = new_revision_nr

    def _info_from_logs(self, logs, checkout_path):
        """Get files and removed lists from logs.
        """        
        files = set()
        removed = set()

        # go from newest to oldest
        logs.reverse()
        
        for log in logs:
            for p in log.strpaths:
                rel_path = p.strpath[len(checkout_path):]
                steps = rel_path.split(self.path.sep)
                # construct py.path to file
                path = self.path.join(*steps)
                if p.action == 'D':
                    removed.add(path)
                else:
                    files.add(path)                
        return files, removed

    def _resolve_path(self, path):
        # resolve any direct conflicts
        for conflict in path.status().conflict:
            mine, other = conflict_info(conflict)
            conflict.write(mine.read())
            self._found(conflict, other.read())
            conflict._svn('resolved')
        # move any status unknown directories away
        for unknown in path.status().unknown:
            if unknown.check(dir=True):
                self._found_container(unknown)
                unknown.remove()

    def _resolve_helper(self, path):
        if not path.check(dir=True):
            return
        # resolve paths in this dir
        self._resolve_path(path)
        for p in path.listdir():
            self._resolve_helper(p)

    def _svn_path(self, path):
        """Turn a (possibly local) path into an SVN path.
        """
        rel_path = path.relto(self.path)
        return self.path.join(*rel_path.split(path.sep))

    def _found_path(self, path):
        """Turn a path into a found path.
        """
        found = self.path.ensure('found', dir=True)
        rel_path = path.relto(self.path)
        return found.join(*rel_path.split(path.sep))

def is_descendant(path, path2):
    """Determine whether path2 is a true descendant of path.

    a path is not a descendant of itself.
    """
    return path2 > path

def conflict_info(conflict):
    path = conflict.dirpath()
    name = conflict.basename
    mine = path.join(name + '.mine')
    name_pattern = name + '.r'
    revs = []
    for rev in path.listdir(name_pattern + '*'):
        revs.append((int(rev.basename[len(name_pattern):]), rev))
    # find the most recent rev
    rev_nr, other = sorted(revs)[-1]
    return mine, other
    
