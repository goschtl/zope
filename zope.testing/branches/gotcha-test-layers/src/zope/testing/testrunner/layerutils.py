from zope.testing.testrunner.find import name_from_layer


def order_by_bases(layers):
    """Order the layers from least to most specific (bottom to top)

    >>> class TestLayer(object):
    ...    def __init__(self, bases, name):
    ...        self.__bases__ = bases
    ...        self.__name__ = name
    ...    def __repr__(self):
    ...        return self.__name__

    A layer without any base:

    >>> zero = TestLayer(bases=(), name='zero')

    A layer with a single base:

    >>> one = TestLayer(bases=(zero, ), name='one')

    Less specific comes first:

    >>> order_by_bases([one, zero])
    [zero, one]
    >>> order_by_bases([zero, one])
    [zero, one]


    Another layer with a single base:

    >>> one_bis = TestLayer(bases=(zero, ), name='one_bis')

    Less specific comes first:

    >>> order_by_bases([one, zero, one_bis])
    [zero, one, one_bis]

    Order of layers of identical specificity does not depend
    on their order in the input:

    >>> order_by_bases([one_bis, zero, one])
    [zero, one, one_bis]
    >>> order_by_bases([one_bis, one, zero])
    [zero, one, one_bis]
    >>> order_by_bases([zero, one_bis, one])
    [zero, one, one_bis]

    Another layer with a single base:

    >>> one_ter = TestLayer(bases=(zero, ), name='one_ter')

    Less specific still comes first:

    >>> order_by_bases([one_bis, one_ter, one, zero])
    [zero, one, one_bis, one_ter]

    Order of layers of identical specificity does still not depend
    on their order in the input:

    >>> order_by_bases([one_ter, one_bis, one, zero])
    [zero, one, one_bis, one_ter]
    >>> order_by_bases([zero, one_ter, one_bis, one])
    [zero, one, one_bis, one_ter]

    A layer with two bases of different specificity:

    >>> two = TestLayer(bases=(zero, one), name='two')

    Ordered by inverse specificity:

    >>> order_by_bases([two, one, zero])
    [zero, one, two]
    >>> order_by_bases([zero, two, one])
    [zero, one, two]
    >>> order_by_bases([two, zero, one])
    [zero, one, two]

    Another layer with two bases of different specificity:

    >>> two_bis = TestLayer(bases=(zero, one_bis), name='two_bis')

    >>> order_by_bases([two, two_bis, one, zero])
    [zero, one, two, two_bis]
    >>> order_by_bases([two_bis, two, one, zero])
    [zero, one, two, two_bis]

    >>> order_by_bases([one_bis, two_bis, two, one, zero])
    [zero, one, one_bis, two, two_bis]

    >>> three = TestLayer(bases=(one_bis, two), name='three')

    >>> order_by_bases([one_bis, two_bis, three, two, one, zero])
    [zero, one, one_bis, two, two_bis, three]
    >>> order_by_bases([three, one_bis, two_bis, two, one, zero])
    [zero, one, one_bis, two, two_bis, three]
    >>> order_by_bases([one_bis, three, two_bis, two, one, zero])
    [zero, one, one_bis, two, two_bis, three]
    >>> order_by_bases([one_bis, two_bis, two, three, one, zero])
    [zero, one, one_bis, two, two_bis, three]

    Another layer without any base:

    >>> other_zero = TestLayer(bases=(), name='other_zero')

    >>> order_by_bases([other_zero, zero])
    [other_zero, zero]
    >>> order_by_bases([zero, other_zero])
    [other_zero, zero]

    Another layer with this new base:

    >>> other_one = TestLayer(bases=(other_zero, ), name='other_one')

    >>> order_by_bases([one, other_one])
    [one, other_one]
    >>> order_by_bases([one, other_one])
    [one, other_one]

    A layer with the two bases:

    >>> both_one = TestLayer(bases=(zero, other_zero, ), name='both_one')

    >>> order_by_bases([one, other_one, both_one])
    [one, other_one, both_one]
    >>> order_by_bases([one, other_one, both_one])
    [one, other_one, both_one]
    >>> order_by_bases([both_one, one, other_one])
    [one, other_one, both_one]
    >>> order_by_bases([one, both_one, other_one])
    [one, other_one, both_one]

    Another layer with the two bases:

    >>> both_one_bis = TestLayer(bases=(zero, other_zero, ),
    ...     name='both_one_bis')

    >>> order_by_bases([both_one_bis, one, other_one, both_one])
    [one, other_one, both_one, both_one_bis]
    >>> order_by_bases([one, both_one_bis, other_one, both_one])
    [one, other_one, both_one, both_one_bis]
    >>> order_by_bases([both_one, one, both_one_bis, other_one])
    [one, other_one, both_one, both_one_bis]
    >>> order_by_bases([one, both_one, other_one, both_one_bis])
    [one, other_one, both_one, both_one_bis]

    >>> order_by_bases([two, both_one_bis, one, other_one, both_one])
    [one, other_one, both_one, both_one_bis, two]
    >>> order_by_bases([one, two, both_one_bis, other_one, both_one])
    [one, other_one, both_one, both_one_bis, two]
    >>> order_by_bases([both_one, one, two, both_one_bis, other_one])
    [one, other_one, both_one, both_one_bis, two]
    >>> order_by_bases([one, both_one, two, other_one, both_one_bis])
    [one, other_one, both_one, both_one_bis, two]

    """
    named_layers = [(name_from_layer(layer), layer) for layer in layers]
    named_layers.sort()
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
