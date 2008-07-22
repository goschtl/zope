import soup
import session as tx
import interfaces

class dictproxy(dict):
    """Dictionary proxy.

    Proxies non-mapped attributes to an internal dictionary.
    """
    
    def __init__(self, owner):
        assert interfaces.IMapped.providedBy(owner)
        self.owner = owner

    def _is_mapped(self, key):
        owner = self.owner
        return key.startswith('_v_') or \
               key in owner.__class__.__dict__ or \
               key in owner._sa_class_manager.keys()
    
    def __getitem(self, key):
        if self._is_mapped(key):
            return dict.__getitem__(key)

        if self.owner.dict is None:
            raise KeyError(key)
        
        return self.owner.dict[key]
        
    def __setitem__(self, key, value):
        if self._is_mapped(key):
            dict.__setitem__(self, key, value)
        else:
            if self.owner.dict is None:
                self.owner.dict = {key: value}
            else:
                self.owner.dict[key] = value

    def __repr__(self):
        return "<dictproxy %s>" % dict.__repr__(self)
