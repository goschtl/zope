class MapKey(object):
    def __init__(self, key, parents=()):
        self.key = key
        self.parents = parents
        # we need Python's mro, but we don't have classes. We create
        # some with the same structure as our parent structure. then we
        # get the mro
        self._mro_helper = type('fake_type',
                                tuple(parent._mro_helper for
                                      parent in parents),
                                {'mapkey': self})
        # we then store the map keys for the mro (without the last
        # entry, which is always object)
        self._parent_mapkeys = [
            base.mapkey for base in self._mro_helper.__mro__[:-1]]

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return self.key == other.key

    def __repr__(self):
        return "<MapKey: %r>" % self.key

class Map(dict):
    def __getitem__(self, key):
        for mapkey in key._parent_mapkeys:
            try:
                return super(Map, self).__getitem__(mapkey)
            except KeyError:
                pass
        raise KeyError(key)


