# -*- coding: UTF-8 -*-

#support functions

import string

def islist(data):
    u"""is the parameter list-like?"""
    try:
        data[0]
        return not isinstance(data, basestring)
    except:
        return False


def isdict(data):
    u"""is the parameter dict-like?"""
    try:
        data.keys()
        #BTree miatt nem kene isinstance
        return True
    except:
        return False

class Translator:
    u"""character translator"""
    
    allchars = string.maketrans('','')
    def __init__(self, frm='', to='', delete='', keep=None):
        if len(to) == 1:
            to = to * len(frm)
        self.trans = string.maketrans(frm, to)
        if keep is None:
            self.delete = delete
        else:
            self.delete = self.allchars.translate(self.allchars, keep.translate(self.allchars, delete))
    def __call__(self, s):
        return s.translate(self.trans, self.delete)

keepPrintableTrans = Translator(keep=string.printable)

def safe_str(uncode):
    u"""unicode and any-character safe str()"""
    
    if not isinstance(uncode, basestring):
        uncode = unicode(uncode)
    try:
        x=uncode.encode('ascii','replace')
    except UnicodeDecodeError:
        uncode = keepPrintableTrans(uncode)
        x=uncode.encode('ascii','replace')
    return x

class curry:
    """Taken from the Python Cookbook, this class provides an easy way to
    tie up a function with some default parameters and call it later.
    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52549 for more.
    """
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.pending = args[:]
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        if kwargs and self.kwargs:
            kw = self.kwargs.copy()
            kw.update(kwargs)
        else:
            kw = kwargs or self.kwargs
        return self.func(*(self.pending + args), **kw)