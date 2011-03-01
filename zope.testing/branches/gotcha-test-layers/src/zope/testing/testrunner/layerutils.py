##############################################################################
#
# Copyright (c) 2004-2008 Zope Foundation and Contributors.
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
"""Layer helpers
"""
from zope.testing.testrunner.find import name_from_layer


def order_by_bases(layers):
    """Order the layers from least to most specific (bottom to top)

    >>> class Base(object):
    ...    __bases__ = ()
    ...    @property
    ...    def __name__(self):
    ...        return self.__class__.__name__
    ...    def __repr__(self):
    ...        return self.__name__

    A layer without any base:

    >>> class Zero(Base):
    ...     pass
    >>> zero = Zero()

    A layer with a single base:

    >>> class One(Base):
    ...    __bases__ = (zero, )
    >>> one = One()

    Less specific comes first:

    >>> order_by_bases([one, zero])
    [Zero, One]


    Another layer with a single base:

    >>> class OneBis(Base):
    ...    __bases__ = (one, )
    >>> one_bis = OneBis()

    Less specific comes first:

    >>> order_by_bases([one, zero, one_bis])
    [Zero, One, OneBis]

    Order of layers of identical specificity does not depend
    on their order in the input:

    >>> order_by_bases([one_bis, zero, one])
    [Zero, One, OneBis]
    >>> order_by_bases([one_bis, one, zero])
    [Zero, One, OneBis]
    >>> order_by_bases([zero, one_bis, one])
    [Zero, One, OneBis]

    Another layer with a single base:

    >>> class OneTer(Base):
    ...    __bases__ = (zero, )
    >>> one_ter = OneTer()

    Less specific still comes first:

    >>> order_by_bases([one_bis, one_ter, one, zero])
    [Zero, OneTer, One, OneBis]

    Order of layers of identical specificity does still not depend
    on their order in the input:

    >>> order_by_bases([one_ter, one_bis, one, zero])
    [Zero, OneTer, One, OneBis]
    >>> order_by_bases([zero, one_ter, one_bis, one])
    [Zero, OneTer, One, OneBis]

    A layer with two bases of different specificity:

    >>> class Two(Base):
    ...    __bases__ = (zero, one)
    >>> two = Two()

    Ordered by inverse specificity:

    >>> order_by_bases([two, one, zero])
    [Zero, One, Two]
    >>> order_by_bases([zero, two, one])
    [Zero, One, Two]
    >>> order_by_bases([two, zero, one])
    [Zero, One, Two]

    Another layer with two bases of different specificity:

    >>> class TwoBis(Base):
    ...    __bases__ = (zero, one_bis)
    >>> two_bis = TwoBis()

    >>> order_by_bases([two, two_bis, one, zero])
    [Zero, One, Two, TwoBis]
    >>> order_by_bases([two_bis, two, one, zero])
    [Zero, One, Two, TwoBis]

    >>> order_by_bases([one_bis, two_bis, two, one, zero])
    [Zero, One, OneBis, Two, TwoBis]

    >>> class Three(Base):
    ...    __bases__ = (two, one_bis)
    >>> three = Three()

    >>> order_by_bases([one_bis, two_bis, three, two, one, zero])
    [Zero, One, OneBis, Two, TwoBis, Three]
    """
    named_layers = [(name_from_layer(layer), layer) for layer in layers]
    named_layers.sort()
    named_layers.reverse()
    # Store layers along with their specificity measured by numbers of
    # sublayers.
    all_layers = {}
    for name, layer in named_layers:
        gathered = []
        gather_layers(layer, gathered)
        index = len(gathered)
        some_layers = all_layers.setdefault(index, [])
        some_layers.append(gathered)
    keys = all_layers.keys()
    keys.sort()
    # Gather them all starting by the least specific.
    gathered = []
    for key in keys:
        for some_layers in all_layers[key]:
            gathered.extend(some_layers)
    seen = {}
    result = []
    for layer in gathered:
        if layer not in seen:
            seen[layer] = 1
            if layer in layers:
                result.append(layer)
    return result


def gather_layers(layer, result):
    if layer is not object:
        result.append(layer)
    for b in layer.__bases__:
        gather_layers(b, result)
