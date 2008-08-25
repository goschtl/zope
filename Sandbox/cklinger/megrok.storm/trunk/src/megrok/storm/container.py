from storm.exceptions import WrongStoreError, NoStoreError, ClassInfoError
from storm.store import Store, get_where_for_args
from storm.expr import (
    Select, Column, Exists, ComparableExpr, LeftJoin, SQLRaw,
    compare_columns, compile)
from storm.info import get_cls_info, get_obj_info


##
from storm.references import ReferenceSet, BoundIndirectReferenceSet, BoundReferenceSet

import grok

class CBoundReferenceSet(BoundReferenceSet, grok.Model):
    def traverse(self, name):
	print name
	print self.find(id=int(name))
	return self.find(id=int(name)).one()

class CReferenceSet(ReferenceSet):

    def __get__(self, local, cls=None):
        if local is None:
            return self

        # Don't use local here, as it might be security proxied or something.
        local = get_obj_info(local).get_obj()

        if self._relation1 is None:
            self._build_relations(local.__class__)

        #store = Store.of(local)
        #if store is None:
        #    return None

        if self._relation2 is None:
            return CBoundReferenceSet(self._relation1, local, self._order_by)
        else:
            return BoundIndirectReferenceSet(self._relation1,
                                             self._relation2, local,
                                             self._order_by)

