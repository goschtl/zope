
traditional = [
    (1024 ** 5, 'P'),
    (1024 ** 4, 'T'), 
    (1024 ** 3, 'G'), 
    (1024 ** 2, 'M'), 
    (1024 ** 1, 'K'),
    (1024 ** 0, 'B')
    ]

si = [
    (1000 ** 5, 'P'),
    (1000 ** 4, 'T'), 
    (1000 ** 3, 'G'), 
    (1000 ** 2, 'M'), 
    (1000 ** 1, 'K'),
    (1000 ** 0, 'B')
    ]

def size(bytes, system=traditional):
    """Human-readable file size.

    Using the traditional system, where a factor of 1024 is used::
    
    >>> size(10)
    '10B'
    >>> size(100)
    '100B'
    >>> size(1000)
    '1000B'
    >>> size(2000)
    '1K'
    >>> size(10000)
    '9K'
    >>> size(20000)
    '19K'
    >>> size(100000)
    '97K'
    >>> size(200000)
    '195K'
    >>> size(1000000)
    '976K'
    >>> size(2000000)
    '1M'
    
    Using the SI system, with a factor 1000::

    >>> size(10, system=si)
    '10B'
    >>> size(100, system=si)
    '100B'
    >>> size(1000, system=si)
    '1K'
    >>> size(2000, system=si)
    '2K'
    >>> size(10000, system=si)
    '10K'
    >>> size(20000, system=si)
    '20K'
    >>> size(100000, system=si)
    '100K'
    >>> size(200000, system=si)
    '200K'
    >>> size(1000000, system=si)
    '1M'
    >>> size(2000000, system=si)
    '2M'
    
    """
    for factor, suffix in system:
        if bytes >= factor:
            break
    return str(int(bytes/factor)) + suffix

