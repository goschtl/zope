from logging import getLogger
from zope.interface import implements
from z3c.indexing.dispatch.interfaces import IQueueReducer
from z3c.indexing.dispatch.constants import INDEX, UNINDEX

debug = getLogger('z3c.indexing.dispatch.reducer').debug

class QueueReducer(object):
    """Reduce a queue of index operations."""
    
    implements(IQueueReducer)

    def optimize(self, queue):
        res = {}
        debug('start reducing %d item(s): %r', len(queue), queue)

        for iop, obj, iattr in queue:
            oid = hash(obj)
            op, dummy, attr = res.get(oid, (0, obj, iattr))
            # If we are going to delete an item that was added in this transaction, ignore it
            if op == INDEX and iop == UNINDEX:
                del res[oid]
            else:
                # Operators are -1, 0 or 1 which makes it safe to add them
                op += iop
                op = min(max(op,UNINDEX), INDEX) # operator always between -1 and 1

                # Handle attributes, None means all fields, and takes presedence
                if isinstance(attr, (tuple,list)) and isinstance(iattr, (tuple,list)):
                    attr = tuple(set(attr + iattr))
                else:
                    attr = None

                res[oid] = (op, obj, attr)

        debug('finished reducing; %d item(s) in queue...', len(res))

        return res.values()
