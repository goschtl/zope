import os
from os.path import join, abspath, dirname

def products():
    prefix = abspath(dirname(__file__))
    import Products
    Products.__path__.append(join(prefix, 'products'))
