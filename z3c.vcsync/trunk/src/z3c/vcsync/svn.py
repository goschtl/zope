import py
from datetime import datetime

# amount of log entries to search through in a single step
LOG_STEP = 5

class SvnCheckout(object):
    """A checkout for SVN.

    This is a simplistic implementation. Advanced implementations
    might check what has been changed in an SVN update and change the
    load() method to only bother to load changed (or added or removed)
    data. Similarly save() could be adjusted to only save changed
    data.
    
    It is assumed to be initialized with py.path.svnwc
    """

    def __init__(self, path):
        self.path = path
        self._files = set()
        self._removed = set()
        self._updated = False
        
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
        self._updated = False
        
    def resolve(self):
        pass

    def commit(self, message):
        self.path.commit(message)

    def files(self, dt):
        self._update_files(dt)
        return list(self._files)
    
    def removed(self, dt):
        # XXX strictly speaking update_files caching only works
        # if dt arg is always the same as in files..
        self._update_files(dt)
        return list(self._removed)

    def _update_files(self, dt):
        """Go through svn log and update self._files and self._removed.
        """
        if self._updated:
            return
        
        files = set()
        removed = set()
        checkout_path = self._checkout_path()

        # step backwards through svn log until we're done
        rev = int(self.path.status().rev)
        while True:
            prev_rev = rev - LOG_STEP
            logs = self.path.log(prev_rev, rev, verbose=True)
            done = self._update_from_logs(logs, dt, checkout_path,
                                          files, removed)
            if done:
                break
            rev = prev_rev - 1
        
        self._files = files
        self._removed = removed
        self._updated = True

    def _update_from_logs(self, logs, dt, checkout_path, files, removed):
        """Update files and removed from logs.

        Return True if we're done.
        """
        for log in logs:
            log_dt = datetime.fromtimestamp(log.date)
            if log_dt < dt:
                return True
            for p in log.strpaths:
                rel_path = p.strpath[len(checkout_path):]
                steps = rel_path.split(self.path.sep)
                # construct py.path to file
                path = self.path.join(*steps)
                if p.action == 'D':
                    removed.add(path)
                else:
                    files.add(path)                
        return False
    
