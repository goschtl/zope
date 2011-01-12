##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
try:
    import simplejson as json
except ImportError:
    import json

import persistent

class Persistent(persistent.Persistent):

    def _dozodb_get_client_state(self):
        return self.__getstate__()

    def _dozodb_set_client_state(self, state):
        self.__setstate__(state)

    @classmethod
    def _dozodb_new(class_):
        return class_.__new__(class_)

class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, persistent.Persistent):
            if not hasattr(obj, '_dozodb_get_client_state'):
                raise TypeError(
                    "Object doesn't support client serialization",
                    obj)
            # XXX maybe we should use _p_ref here. Would need js change
            return dict(_p_oid=obj._p_oid.encode('hex'))
        return json.JSONEncoder.default(self, obj)

def _result(**o):
    return json.dumps(o, cls=Encoder)

def _serialize(ob):
    state = ob._dozodb_get_client_state()
    state.update(dict(
        _p_oid = ob._p_oid.encode('hex'),
        _p_serial = ob._p_serial.encode('hex'),
        ))
    return state

def load(connection, _p_oid):
    return _result(
        item=_serialize(connection.get(_p_oid.decode('hex')))
        )

def fetched(size, items):
    return _result(items=[_serialize(item) for item in items], size=size)

otypes = list, dict
def save(app, json_string):

    #import pdb; pdb.set_trace()

    changes = json.loads(json_string)

    changed = dict((item['_p_oid'], item) for item in changes['changed'])
    updated = [oid for oid in changed if not oid.startswith('new')]
    inserted = changes['inserted']

    new_ids = {}

    def cleanup(data):
        if isinstance(data, list):
            return map(cleanup, data)
        if not isinstance(data, dict):
            return data

        ref = data.get('_p_ref')
        if ref:
            item = changed.pop(ref, None)
            if item is not None:
                return cleanup(item)
            oid = new_ids.get(ref) or ref.decode('hex')
            return app.connection.get(oid)

        oid = data.pop('_p_oid')
        if oid:
            changed.pop(oid, None)
            if oid.startswith('new'):
                ob = app.factory(data)._dozodb_new()
                app.connection.add(ob)
                new_ids[oid] = ob._p_oid
            else:
                oid = oid.decode('hex')
                ob = app.connection.get(oid)
                ob._p_activate()
                ob._p_changed = 1
                ob._p_serial = data.pop('_p_serial').decode('hex')

        for name, value in data.items():
            if isinstance(value, otypes):
                value = cleanup(value)
                data[name] = value

        if oid:
            ob._dozodb_set_client_state(data)
            return ob

        return data

    for oid in updated + inserted:
        if oid in changed:
            cleanup(changed[oid])

    if changed:
        raise ValueError("Unreachable new objects")

    if inserted:
        app.insert([app.connection.get(new_ids[i]) for i in inserted])

    # XXX it's annoying that we have to commit here, but we need the
    # committed serials. :/  Maybe we can think of something better
    # later, especially when we deal with invalidations.
    app.connection.transaction_manager.commit()

    updates = []
    for (old, oid) in new_ids.iteritems():
        ob = app.connection.get(oid)
        ob._p_activate()
        updates.append(dict(_p_oid=oid.encode('hex'), _p_id=old,
                            _p_serial=ob._p_serial.encode('hex')
                            ))
    for oid in updated:
        ob = app.connection.get(oid.decode('hex'))
        ob._p_activate()
        updates.append(dict(_p_oid=oid,
                            _p_serial=ob._p_serial.encode('hex')
                            ))

    return json.dumps(dict(updates=updates))
