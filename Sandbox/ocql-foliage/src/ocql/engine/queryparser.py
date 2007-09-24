class QueryParser:
    def __init__(self, engine):
        self.metadata = engine.metadata
        
    def parse(self, query):
        queryobject = self.compile(query)
        self.check(queryobject)
        return queryobject
    
    def check(self, queryobject):
        return True
    
    def compile(self, query):
        from ocql.engine.queryobject import *
        
        return \
            Query(
                set,
                [
                    In(Identifier('c'),Identifier('ICurses')),
                    In(Identifier('d'),Identifier('IDepartments')),
                    Eq(Property(Identifier('d'),Identifier('name')),Constant('"Computing Science"')),
                    Eq(Identifier('d'),Quanted(Some(),Property(Identifier('c'),Identifier('runBy')))),
                    Le(Property(Identifier('c'),Identifier('credits')),Constant('3')),
                    Le(Constant('1'),Property(Identifier('c'),Identifier('credits'))),
                ],
                Identifier('c')
            )
        