import py

from z3c.vcsync.vc import CheckoutBase

class SvnCheckout(CheckoutBase):
    """A checkout for SVN.

    This is a simplistic implementation. Advanced implementations
    might check what has been changed in an SVN update and change the
    load() method to only bother to load changed (or added or removed)
    data. Similarly save() could be adjusted to only save changed
    data.
    
    It is assumed to be initialized with py.path.svnwc
    """

    def __init__(self, path):
        super(SvnCheckout, self).__init__(path)
        self._log_info = {'R':[], 'A':[], 'M':[]}

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
        original_rev = int(self.path.status().rev)

        self.path.update()
    
        now_rev = int(self.path.status().rev)
        logs = self.path.log(now_rev, original_rev, verbose=True)

        checkout_path = self._checkout_path()
        log_info = {'R': [], 'A': [], 'M':[]}
        for log in logs:
            for p in log.strpaths:
                rel_path = p.strpath[len(checkout_path):]
                steps = rel_path.split(self.path.sep)
                # construct py.path to file
                path = self.path.join(*steps)
                log_info[p.action].append(path)
        self._log_info = log_info
        
    def resolve(self):
        pass

    def commit(self, message):
        self.path.commit(message)

    def added(self):
        return self._log_info['A']
    
    def deleted(self):
        return self._log_info['R']

    def modified(self):
        return self._log_info['M']

        
