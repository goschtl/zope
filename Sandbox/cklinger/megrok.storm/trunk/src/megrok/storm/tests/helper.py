from storm.locals import *

class Person(object):
    __storm_table__ = "person"

    name = Unicode(primary=True)
    age = Int()
