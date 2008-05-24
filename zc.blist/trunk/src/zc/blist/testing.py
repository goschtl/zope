import random

import zc.blist

def checkIndex(ix, b, previous, previous_ix=0):
    computed = 0
    if len(previous) < previous_ix+1:
        previous.append(None)
        assert len(previous) >= previous_ix + 1
    # assert isinstance(ix, zc.blist.Index)
    assert b.data is ix or len(ix) <= b.index_size
    assert b.data is ix or len(ix) >= b.index_size // 2
    assert ix.minKey() == 0
    for k, v in ix.items():
        v = b._mapping[v]
        assert computed == k
        assert v.parent == ix.identifier
        p = previous[previous_ix]
        if p is not None:
            p = p.identifier
        assert v.previous == p
        assert (v.previous is None or
                previous[previous_ix].next == v.identifier)
        assert (v.next is None or
                b._mapping[v.next].previous == v.identifier)
        computed += v.contained_len(b)
        if isinstance(v, zc.blist.Index):
            checkIndex(v, b, previous, previous_ix+1)
        else:
            assert isinstance(v, zc.blist.Bucket)
            assert len(v) <= b.bucket_size
            assert (len(v) >= b.bucket_size // 2)
        previous[previous_ix] = v
    
def matches(b, result):
    assert list(b) == result, repr(list(b)) + ' != ' + repr(result)
    assert len(b) == len(result)
    assert list(b[::-1]) == list(reversed(result))
    res = []
    bad = [(i, (b_i, r_i)) for (i, b_i, r_i) in
           ((i, b[i], result[i]) for i in range(len(b)))
           if b_i != r_i]
    assert not bad, 'getitems do not match on these indices: ' + repr(bad)
    # we'll check the buckets internally while we are here
    assert b.data.parent is None
    assert b.data.previous is None and b.data.next is None
    if isinstance(b.data, zc.blist.Index):
        checkIndex(b.data, b, [None])
    return True

def checkCopies(one, two):
    one_diff = list(
        one.family.IO.difference(one._mapping, two._mapping))
    for k in one_diff:
        data = one._mapping[k]
        assert one in data.collections
        assert two not in data.collections
    two_diff = list(
        one.family.IO.difference(two._mapping, one._mapping))
    for k in two_diff:
        data = two._mapping[k]
        assert two in data.collections
        assert one not in data.collections
    diff = []
    for k, v in one._mapping.items():
        alt = two._mapping.get(k)
        if alt is None:
            assert k in one_diff
            continue
        if alt is v:
            assert one in v.collections and two in v.collections
        else:
            assert (one in v.collections and
                    one not in alt.collections and
                    two in alt.collections and
                    two not in v.collections)
            diff.append((k, v, alt))
    return one_diff, two_diff, diff

def RandomGenerator():
    while 1:
        yield random.randint(-sys.maxint, sys.maxint)

def StringGenerator(src='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    "infinite-ish unique string generator"
    for el in src:
        yield el
    for pre in StringGenerator(src):
        for el in src:
            yield pre + el

def NumberGenerator(number=0, interval=1):
    "infinite-ish unique number generator"
    while 1:
        yield number
        number += interval