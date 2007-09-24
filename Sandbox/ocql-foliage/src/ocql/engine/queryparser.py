#
# Stub of query parser at the moment
#
# A parser is easy to write
# at the moment this returns a fixed Query object
#

from ocql.engine.queryobject import *

#this is the wired query:
"""
set [
    c in ICurses;
    d in IDepartments;
    d.name="Computing Science";
    d = some c.runBy;
    1<=c.credits;
    c.credits <= 3
    | c ]
"""

WIRED = Query(
    set,
    [
        In(Identifier('c'),Identifier('ICurses')),
        In(Identifier('d'),Identifier('IDepartments')),
        Eq(
            Property(Identifier('d'),Identifier('name')),
            StringConstant('"Computing Science"')
            ),
        Eq(
            Identifier('d'),
            Quanted(
                Some(),
                Property(Identifier('c'),Identifier('runBy'))
                )
            ),
        Le(
            NumericConstant('1'),
            Property(Identifier('c'),Identifier('credits'))
            ),
        Le(
            Property(Identifier('c'),Identifier('credits')),
            NumericConstant('3')
            ),
    ],
    Identifier('c')
)

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
        return WIRED