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
        self._log_info = {'D':[], 'A':[], 'M':[]}
      
    def up(self):
        original_rev = self.path.status().rev

        self.path.update()

        now_rev = self.path.status().rev
        logs = self.path.log(now_rev, original_rev + 1, verbose=True)
        log_info = {'D': [], 'A': [], 'M':[]}
        for log in logs:
            entries = log_info[log.action]
            for p in log.strpaths:
                entries.append(py.path.local(p.strpath))
        self._log_info = log_info
        
    def resolve(self):
        pass

    def commit(self, message):
        self.path.commit(message)

    def added(self):
        return self._log_info['A']
    
    def deleted(self):
        return self._log_info['D']

    def modified(self):
        return self._log_info['M']

        
