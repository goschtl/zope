import json
import persistent

class Persistent(persistent.Persistent):

    def _dozodb_get_client_state(self):
        return self.__getstate__()

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, persistent.Persistent):
            if not hasattr(obj._dozodb_get_client_state):
                raise TypeError(
                    "Object doesn't support client serialization",
                    obj)
            return dict(_p_oid=obj._p_oid.encode('hex'))
        return json.JSONEncoder.default(self, obj)

def _result(**o):
    return json.dumps(o, cls=Encoder)

def _serialize(ob):
    state = ob._dozodb_get_client_state()
    state.update(dict(
        _p_oid = self._p_oid.encode('hex'),
        _p_serial = self._p_serial.encode('hex'),
        ))
    return state

def load(connection, _p_oid):
    return result(
        item=_serialize(c.get(_p_oid.decode('hex')))
        )

def fetched(items):
    return result(items=[_serialize(item) for item in items])


