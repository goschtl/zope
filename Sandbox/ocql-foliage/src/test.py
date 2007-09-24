from ocql import OCQLEngine
engine = OCQLEngine()

query = engine.compile("""set [ c in ICurses; d in IDepartments; d.name="Computing Science"; d = some c.runBy; 1<=c.credits; c.credits <= 3 | c ]""") 
print query.execute() 

#q=Iter(set, Lambda('d', 
#        If(Eq(Identifier('d.name'),Identifier('"Computing Science"')),
#            Single(set,Identifier('x')),
#            Empty(set,None)
#        )
#    ), Collection('IDepartments'))
#
#q=Iter(set,
#    If('d.name="Computing Science"',
#        Select(set, Lambda('c',
#            And(Reduce(set, 'False', Lambda('d','d=i'), Or, 'c.runBy'),
#                '1<=c.credits',
#                'c.credits<=3')),
#            ICurses),
#        Empty(set,None)), 
#    Collection('IDepartments'))
#
#m = q.compile()
#print m
#c = compile(m,'','eval')
#print eval(c)
