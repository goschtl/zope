import py
from datetime import datetime

class SvnCheckout(object):
    """A checkout for SVN.

    It is assumed to be initialized with py.path.svnwc
    """

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
        self.path.update()
        self._updated_revision_nr = None
        
    def resolve(self):
        _resolve_helper(self.path)

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
    
    def _update_files(self, revision_nr):
        """Go through svn log and update self._files and self._removed.
        """
        new_revision_nr = int(self.path.status().rev)
        if self._updated_revision_nr == new_revision_nr:
            return
        # logs won't include revision_nr itself, but that's what we want
        if new_revision_nr > revision_nr:
            logs = self.path.log(revision_nr, new_revision_nr, verbose=True)
        else:
            # the log function always seem to return at least one log
            # entry (the latest one). This way we skip that check if not
            # needed
            logs = []
        checkout_path = self._checkout_path()
        files, removed = self._info_from_logs(logs, checkout_path)

        self._files = files
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

def _resolve_helper(path):
    for p in path.listdir():
        if not p.check(dir=True):
            continue
        try:
            for conflict in p.status().conflict:
                mine = p.join(conflict.basename + '.mine')
                conflict.write(mine.read())
                conflict._svn('resolved')
        # XXX This is a horrible hack to skip status of R. This
        # is not supported by Py 0.9.0, and raises a NotImplementedError.
        # This has been fixed on the trunk of Py.
        # When we upgrade to a new release of Py this can go away
        except NotImplementedError:
            pass
        _resolve_helper(p)
