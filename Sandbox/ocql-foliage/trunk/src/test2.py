import testdb
from ocql.engine.queryobject import *
import operator
import testalgebra
from ocql.ocqlengine import OCQLEngine
from ocql.engine.runnablequery import RunnableQuery

engine = OCQLEngine()

#
# Simple empty query
#
# set [ ]
#
query = "set [ ]"
qo=Query(set, [] ,  Identifier('') )
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ", q.execute()
print "expected:", set([])

#
# Simple SELECT ALL
#
# set [ c in ICurses | c ]
#
query = "[ c in ICurses | c ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
    ] ,Identifier('c'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ", set([ i.name for i in q.execute() ])
print "expected:", set([ "C1" , "C2", "C3" ])

#
# Selecting a property
#
# set [ c in ICurses | c.name ]
#
query = "[ c in ICurses | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set([ "C1" , "C2", "C3"  ])

#
# Filtering -- empty result
#
# set [ c in ICurses , c.credits>3 | c.name ]
#
query = "[ c in ICurses, c.credits>3 | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        Gt(Identifier('c.credits'),Constant('3')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expecter:",set([])

#
# Filtering -- full result
#
# set [ c in ICurses , c.credits<=3 | c.name ]
#
query = "[ c in ICurses, c.credits<=3 | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        Le(Identifier('c.credits'),Constant('3')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set([ "C1" , "C2", "C3" ])

#
# Filtering -- one result
#
# set [ c in ICurses , c.credits=3 | c.name ]
#
query = "[ c in ICurses, c.credits=3 | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        Eq(Identifier('c.credits'),Constant('3')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set([ "C2", "C3" ])

#
# Two filters -- full results
#
# set [ c in ICurses , c.credits<5, c.credits >=1  | c.name ]
#
query = "[ c in ICurses, c.credits<3, c.credits>=1 | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        Lt(Identifier('c.credits'),Constant('5')),
        Ge(Identifier('c.credits'),Constant('1')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set([ "C1", "C2", "C3" ])

#
# Two filters -- one result
#
# set [ c in ICurses , c.credits<=2, 2<=c.credits  | c.name ]
#
query = "[ c in ICurses, c.credits<=2, 2<=c.credits | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        Le(Identifier('c.credits'),Constant('2')),
        Le(Constant('2'),Identifier('c.credits')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set([ "C1" ])

#
# Two filters -- one result
#
# set [ c in ICurses , c.credits>=2, 2>=c.credits  | c.name ]
#
query = "[ c in ICurses, c.credits>=2, 2>=c.credits | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        Ge(Identifier('c.credits'),Constant('2')),
        Ge(Constant('2'),Identifier('c.credits')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set([ "C1" ])

#
# Two filters -- no result
#
# set [ c in ICurses , c.credits=3, c.credits!=3  | c.name ]
#
query = "[ c in ICurses, c.credits=3, c.credits!=3 | c.name ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        Eq(Identifier('c.credits'),Constant('3')),
        Ne(Identifier('c.credits'),Constant('3')),
    ] ,Identifier('c.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set([])

#
# join -- Departments running curses
#
# set [ c in ICurses d, in IDepartments ,  some c.runBy = d  | d.name ]
#
query = "[ c in ICurses, d in IDepartments, d = some c.runBy | d.name  ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        In(Identifier('d'),Identifier('IDepartments')),
        Eq(Identifier('d'),Quanted(Some(),Identifier('c.runBy'))),
    ] ,Identifier('d.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set(['Computing Science', 'Other Department'])

#
# join -- Departments running some 3 credits curses
#
# set [ d in ICurses, c in ICurses, c.credits=3, some c.runBy = d | d.name ]
#
query = "[ c in ICurses, d in IDepartments, c.credits=3, d = some c.runBy | d.name  ]"
qo=Query(set, [
        In(Identifier('c'),Identifier('ICurses')),
        In(Identifier('d'),Identifier('IDepartments')),
        Eq(Identifier('c.credits'),Constant('3')),
        Eq(Identifier('d'),Quanted(Some(),Identifier('c.runBy'))),
    ] ,Identifier('d.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set(['Computing Science'])

#
# join -- Departments running some not 3 credits curses
#
# [ d in IDepartments, cr as [ c in ICurses,  some c.runBy = d | c.credits ], some cr != 3| d.name  ]
#
query = "[ d in IDepartments, cr as set [ c in ICurses,  some c.runBy = d | c.credits ], some cr != 3| d.name  ]"
qo=Query(set, [
        In(Identifier('d'),Identifier('IDepartments')),
        Alias(Identifier('cr'),
            Query(set, [
                In(Identifier('c'),Identifier('ICurses')),
                Eq(Identifier('d'),Quanted(Some(),Identifier('c.runBy'))),
            ], Identifier('c.credits'))),
        Ne(Identifier('cr'),Quanted(Some(),Constant(3))),
    ] ,Identifier('d.name'))
algebra=qo.rewrite(testalgebra)
code=algebra.compile();
compile(code,'<string>','eval')
q = RunnableQuery(engine,algebra,code)

print 
print query
print algebra
print code
print "got:     ",q.execute()
print "expected:",set(['Computing Science'])

#
# join -- Departments running just 3 credits curses
#
# set [ d in ICurses, cr as set [ c in ICurses, some c.runBy = d | c.credits ],  all cr = 3  | d.name ]"
#

