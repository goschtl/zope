#
# Stub of query parser at the moment
#
# A parser is easy to write
# at the moment this returns a fixed Query object
#

import copy
from collections import deque
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

class SymbolContainer:
    def __init__(self):
        self.stack = deque()
        self.stack.append(dict())
    
    def addlevel(self):
        top = self.current()
        new = dict(top)
        self.stack.append(new)
        
        #print 'add'
        #print self.stack
    
    def dellevel(self):
        self.stack.pop()
        
        #print 'del'
        #print self.stack
    
    def current(self):
        return self.stack[-1]

class QueryParser:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = engine.metadata
        
    def parse(self, query):
        queryobject = self.compile(query)
        self.check(queryobject)
        return queryobject
    
    def check(self, queryobject):
        return True
    
    def compile(self, query):
        metadata = self.metadata
        #TODO: f-ing wrong place for this
        metadata.symbols = SymbolContainer()
        
        WIRED = Query(
            metadata,
            set,
            [
                In(
                    metadata,
                    Identifier(metadata,'c'),
                    Identifier(metadata,'ICurses')
                    ),
                In(
                    metadata,
                    Identifier(metadata,'d'),
                    Identifier(metadata,'IDepartments')
                    ),
                Eq(
                    metadata,
                    Property(metadata,
                        Identifier(metadata,'d'),
                        Identifier(metadata,'name')),
                    StringConstant(metadata,'"Computing Science"')
                    ),
                Eq(
                    metadata,
                    Identifier(metadata,'d'),
                    Quanted(
                        metadata,
                        Some(metadata),
                        Property(metadata, 
                            Identifier(metadata, 'c'),
                            Identifier(metadata, 'runBy'))
                        )
                    ),
                Le(
                    metadata,
                    NumericConstant(metadata, '1'),
                    Property(metadata,
                        Identifier(metadata, 'c'),
                        Identifier(metadata, 'credits'))
                    ),
                Le(
                    metadata,
                    Property(metadata,
                        Identifier(metadata, 'c'),
                        Identifier(metadata, 'credits')),
                    NumericConstant(metadata, '3')
                    ),
            ],
            Identifier(metadata, 'c')
        )
        x = WIRED
        #x.setMetadata(self.metadata)
        return x