from zope import interface

from z3c.saconfig import Session

import soup
import transaction

def beforeCommitHook(obj, uuid):
    # unset pending state
    session = Session()
    del session._d_pending[uuid]

    # build instance
    instance = soup.lookup(uuid)

    # update attributes
    soup.update(instance, obj)    

def registerObject(obj, uuid):
    session = Session()

    try:
        pending = session._d_pending.keys()
    except AttributeError:
        pending = ()
    
    if obj not in pending:
        try:
            session._d_pending[uuid] = obj
        except AttributeError:
            session._d_pending = {uuid: obj}

        transaction.get().addBeforeCommitHook(beforeCommitHook, (obj, uuid))
