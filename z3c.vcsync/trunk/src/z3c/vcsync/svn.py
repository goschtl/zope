import py

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
        self._log_info = log_info()
        
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
        original_rev = int(self.path.status().rev) - 10

        self.path.update()
    
        now_rev = int(self.path.status().rev)
        
        if original_rev == now_rev:
            return
        
        logs = self.path.log(original_rev + 1, now_rev, verbose=True)

        checkout_path = self._checkout_path()
        info = log_info()
        for log in logs:
            for p in log.strpaths:
                rel_path = p.strpath[len(checkout_path):]
                steps = rel_path.split(self.path.sep)
                # construct py.path to file
                path = self.path.join(*steps)
                info[p.action].add(path)
        self._log_info = info
        
    def resolve(self):
        pass

    def commit(self, message):
        self.path.commit(message)

    def added(self):
        return list(self._log_info['A'])
    
    def deleted(self):
        return list(self._log_info['D'])

    def modified(self):
        return list(self._log_info['M'].union(self._log_info['R']))

def log_info():
    return {'D': set(), 'R': set(), 'A': set(), 'M': set()}
