

def isASCII(s):
    """ Checks if a string/unicode string contains only ASCII chars.  """

    if isinstance(s, unicode):
        try:
            s.encode('ascii')
            return True
        except UnicodeError:
            return False

    elif isinstance(s, str):
        try:
            unicode(s, 'ascii')
            return True
        except UnicodeError:
            return False

    else:
        raise TypeError('isASCII() requires a string or unicode string')

