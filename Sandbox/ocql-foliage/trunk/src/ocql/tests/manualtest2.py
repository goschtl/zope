import testdb
from ocql.engine.queryobject import *
from ocql.engine.queryparser import SymbolContainer
import operator
import testalgebra
from ocql.ocqlengine import OCQLEngine
from ocql.engine.runnablequery import RunnableQuery

engine = OCQLEngine()

def doone(query, qo, expected):
    print "==============="
    print "query:",query
    
    algebra=qo.rewrite(testalgebra)
    
    print "algebra:",algebra

    code=algebra.compile();
    compile(code,'<string>','eval')
    q = RunnableQuery(engine,algebra,code)
    
    print "code:",code
    print "---------------"
    print "got:     ", q.execute()
    print "expected:", expected


def test2():
    metadata = engine.metadata
    metadata.symbols = SymbolContainer()
    
    #
    # Simple empty query
    #
    # set [ ]
    #
    query = "set [ ]"
    qo=Query(metadata,
             set,
             [] ,
             Identifier(metadata,
                        '') )
    
    doone(query, qo, set([]))
        
    
    metadata.symbols = SymbolContainer()
    #
    # Simple SELECT ALL
    #
    # set [ c in ICurses | c ]
    #
    query = "[ c in ICurses | c ]"
    qo=Query(
        metadata,
        set,
        [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
        ] ,Identifier(metadata,'c') )
    
    doone(query, qo, set([ "C1" , "C2", "C3" ]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Selecting a property
    #
    # set [ c in ICurses | c.code ]
    #
    query = "[ c in ICurses | c.code ]"
    qo=Query(
        metadata,
        set,
        [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
        ] ,Identifier(metadata,'c.code') )
    
    doone(query, qo, set([ "C1" , "C2", "C3"  ]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Filtering -- empty result
    #
    # set [ c in ICurses , c.credits>3 | c.code ]
    #
    query = "[ c in ICurses, c.credits>3 | c.code ]"
    qo=Query(
        metadata,
        set,
        [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Gt(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'3')),
        ] ,Identifier(metadata, 'c.code') )
    
    doone(query, qo, set([]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Filtering -- full result
    #
    # set [ c in ICurses , c.credits<=3 | c.code ]
    #
    query = "[ c in ICurses, c.credits<=3 | c.code ]"
    qo=Query(
        metadata,
        set, [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Le(metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'3')),
        ] ,Identifier(metadata,'c.code'))
    
    doone(query, qo, set([ "C1" , "C2", "C3" ]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Filtering -- one result
    #
    # set [ c in ICurses , c.credits=3 | c.code ]
    #
    query = "[ c in ICurses, c.credits=3 | c.code ]"
    qo=Query(
        metadata,
        set,
        [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Eq(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'3')),
        ] ,Identifier(metadata,'c.code'))
    
    doone(query, qo, set([ "C2", "C3" ]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Two filters -- full results
    #
    # set [ c in ICurses , c.credits<5, c.credits >=1  | c.code ]
    #
    query = "[ c in ICurses, c.credits<3, c.credits>=1 | c.code ]"
    qo=Query(
        metadata,
        set,
        [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Lt(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'5')),
            Ge(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'1')),
        ] ,Identifier(metadata, 'c.code'))
    
    doone(query, qo, set([ "C1", "C2", "C3" ]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Two filters -- one result
    #
    # set [ c in ICurses , c.credits<=2, 2<=c.credits  | c.code ]
    #
    query = "[ c in ICurses, c.credits<=2, 2<=c.credits | c.code ]"
    qo=Query(
        metadata,
        set, [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Le(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'2')),
            Le(
                metadata,
                Constant(metadata,'2'),
                Identifier(metadata,'c.credits')),
        ] ,Identifier(metadata,'c.code'))
    
    doone(query, qo, set([ "C1" ]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Two filters -- one result
    #
    # set [ c in ICurses , c.credits>=2, 2>=c.credits  | c.code ]
    #
    query = "[ c in ICurses, c.credits>=2, 2>=c.credits | c.code ]"
    qo=Query(
        metadata,
        set, [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Ge(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'2')),
            Ge(
                metadata,
                Constant(metadata,'2'),
                Identifier(metadata,'c.credits')),
        ] ,Identifier(metadata,'c.code'))
    
    doone(query, qo, set([ "C1" ]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # Two filters -- no result
    #
    # set [ c in ICurses , c.credits=3, c.credits!=3  | c.code ]
    #
    query = "[ c in ICurses, c.credits=3, c.credits!=3 | c.code ]"
    qo=Query(
        metadata,
        set, [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Eq(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'3')),
            Ne(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'3')),
        ] ,Identifier(metadata,'c.code'))
    
    doone(query, qo, set([]))
    
    
    metadata.symbols = SymbolContainer()
    #
    # join -- Departments running curses
    #
    # set [ c in ICurses d, in IDepartments ,
    # some c.runBy = d  | d.name ]
    #
    query = "[ c in ICurses, d in IDepartments, d = some c.runBy | d.name  ]"
    qo=Query(
        metadata,
        set, [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            In(
                metadata,
                Identifier(metadata,'d'),
                Identifier(metadata,'IDepartments')),
            Eq(
                metadata,
                Identifier(metadata,'d'),
                Quanted(metadata,
                        Some(metadata),
                        Property(metadata, 
                                Identifier(metadata, 'c'),
                                Identifier(metadata, 'runBy'))
                            )),
        ] ,Identifier(metadata,'d.name'))
    
    doone(query, qo, set(['Computing Science', 'Other Department']))
    
    
    metadata.symbols = SymbolContainer()
    #
    # join -- Departments running some 3 credits curses
    #
    # set [ d in ICurses, c in ICurses, c.credits=3, some c.runBy = d | d.name ]
    #
    query = "[ c in ICurses, d in IDepartments, c.credits=3, d = some c.runBy | d.name  ]"
    qo=Query(
        metadata,
        set,
        [
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            In(
                metadata,
                Identifier(metadata,'d'),
                Identifier(metadata,'IDepartments')),
            Eq(
                metadata,
                Identifier(metadata,'c.credits'),
                Constant(metadata,'3')),
            Eq(
                metadata,
                Identifier(metadata,'d'),
                Quanted(
                    metadata,
                    Some(metadata),
                    Property(metadata, 
                                Identifier(metadata, 'c'),
                                Identifier(metadata, 'runBy'))
                            )),
        ] ,Identifier(metadata, 'd.name'))
    
    doone(query, qo, set(['Computing Science']))
    
    
    metadata.symbols = SymbolContainer()
    # join -- Departments running some not 3 credits curses
    #
    # [ d in IDepartments, c in ICurses, some c.runBy = d, some c.credits != 3| d.name ]
    #
    query = """[ d in IDepartments,
    c in ICurses,
    some c.runBy = d, c.credits != 3| d.name ]"""
    qo=Query(
        metadata,
        set,
        [
            In(
                metadata,
                Identifier(metadata,'d'),
                Identifier(metadata,'IDepartments')),
            In(
                metadata,
                Identifier(metadata,'c'),
                Identifier(metadata,'ICurses')),
            Eq(
                metadata,
                Identifier(metadata,'d'),
                Quanted(
                    metadata,
                    Some(metadata),
                    Property(metadata, 
                                Identifier(metadata, 'c'),
                                Identifier(metadata, 'runBy'))
                            )),
            Ne(
                metadata,
                Constant(metadata,'3'),
                Identifier(metadata,'c.credits')),
        ] ,Identifier(metadata,'d.name'))
    
    doone(query, qo, set(['Other department','Computing Science']))
    
    
    metadata.symbols = SymbolContainer()
    #
    #
    # join -- Departments running just 2 credits curses
    #
    # set [ d in IDepartments, every set [ c in ICurses, some c.runBy = d | c.credits ] = 3  | d.name ]
    #
    query = """set [ d in IDepartments,
        every
        set [ c in ICurses, some c.runBy = d | c.credits ] = 2
        | d.name ]"""
    qo=Query(
        metadata,
        set, 
        [
            In(
                metadata,
                Identifier(metadata,'d'),
                Identifier(metadata,'IDepartments')),
            Eq(
                metadata,
                Quanted(
                    metadata,
                    Every(metadata),
                    Query(
                        metadata,
                        set,
                        [
                            In(
                                metadata,
                                Identifier(metadata,'c'),
                                Identifier(metadata,'ICurses')),
                            Eq(
                                metadata,
                                Identifier(metadata,'d'),
                                Quanted(
                                    metadata,
                                    Some(metadata),
                                    Property(metadata, 
                                        Identifier(metadata, 'c'),
                                        Identifier(metadata, 'runBy'))
                                    )),
                        ], Identifier(metadata, 'c.credits')
                        )
                ),Constant(metadata,'2')),
        ] ,Identifier(metadata,'d.name'))
    
    doone(query, qo, set(['Other department']))
    
    
    #metadata.symbols = SymbolContainer()
    ##
    ##
    ## alias
    ##
    ## set [ c in ICurses, a as c.code  | a ]
    ##
    #query = """set [ c in ICurses, a as c.code  | a ]"""
    #
    #qo=Query(
    #    metadata,
    #    set,
    #    [
    #        In(
    #            metadata,
    #            Identifier(metadata,'c'),
    #            Identifier(metadata,'ICurses')),
    #        Alias(
    #            metadata,
    #            Identifier(metadata,'a'),
    #            Property(metadata, 
    #                 Identifier(metadata, 'c'),
    #                 Identifier(metadata, 'code')))
    #    ] ,Identifier(metadata,'c') )
    #
    #doone(qo, set(['C1','C2','C3']))

if __name__ == "__main__":
    test2()
