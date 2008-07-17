from zope import interface

from z3c.saconfig import Session

import transaction

def COPY_CONCRETE_TO_INSTANCE(uuid):
    return COPY_CONCRETE_TO_INSTANCE, uuid

def COPY_VALUE_TO_INSTANCE(uuid, name):
    return COPY_VALUE_TO_INSTANCE, uuid, name

def addBeforeCommitHook(token, value, hook):
    session = Session()

    try:
        pending = session._d_pending.keys()
    except AttributeError:
        pending = ()

    if token in pending:
        session._d_pending[token] = value
    else:
        try:
            session._d_pending[token] = value
        except AttributeError:
            session._d_pending = {token: value}

        def remove_and_call(*args):
            hook(*args)
            del session._d_pending[token]
            
        transaction.get().addBeforeCommitHook(remove_and_call, ())
