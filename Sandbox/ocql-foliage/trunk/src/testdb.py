from ocql.engine import metadata

# schema
class ICurses:
    pass

class IDepartments:
    pass

class MClass(metadata.MetaType):
    def __init__(self, klass):
        self.klass = klass

    def is_collection(self):
        return True

    def get_type(self):
        return set
    
    def get_contained(self):
        return self.klass
    
class MType(metadata.MetaType):
    def __init__(self, klass, collection_type=None):
        self.klass = klass
        self.collection_type = collection_type

    def is_collection(self):
        return (self.collection_type is not None)

    def get_type(self):
        return self.collection_type
    
    def get_contained(self):
        return self.klass

class Department(object):
    def __init__(self, name):
        self.name = name

class Curses(object):
    def __init__(self, name, runBy, credits):
        self.name = name
        self.runBy = runBy
        self.credits = credits

D1 = Department("Computing Science")
D2 = Department("Other department")
D3 = Department("Department without curse")

C1 = Curses("C1", runBy = set([D1, D2]), credits=2)
C2 = Curses("C2", runBy = set(), credits=3)
C3 = Curses("C3", runBy = set([D1]), credits=3)

# metadata
class TestMetadata(metadata.Metadata):
    db = {
            'IDepartments': [D1, D2],
            'ICurses': [C1, C2, C3]
        }
    classes = {
            'IDepartments': MClass(ICurses),
            'ICurses': MClass(IDepartments),
            }
    properties = {
                'IDepartments': { 'name': str },
                'ICurses': {
                        'runBy': MType(IDepartments,set),
                        'credits': MType(int)
                },
            }
    
    def getAll(self, klass):
        x=self.db[klass]
        return x
    
    def get_class(self, name):
        return classes[name]
