import zc.sharing.interfaces
import ZODB.FileStorage.FileStorage

def evolve(context):
    # specifically for FileStorage, since all legacy instances are FileStorage
    storage = context.connection.db()._storage
    if not isinstance(storage, ZODB.FileStorage.FileStorage):
        return
    key = None
    next_oid = 0
    while next_oid is not None:
        oid, tid, data, next_oid = storage.record_iternext(key)
        obj = context.connection.get(oid)
        sharing = zc.sharing.interfaces.IBaseSharing(obj, None)
        if sharing is not None:
            try:
                data = sharing.annotations.pop('instranet.sharing.sharing')
            except KeyError:
                pass
            else:
                sharing.annotations['zc.sharing.sharing'] = data
        key = next_oid
