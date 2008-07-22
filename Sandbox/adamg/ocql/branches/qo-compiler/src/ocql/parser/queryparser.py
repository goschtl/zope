# -*- coding: UTF-8 -*-

"""Parse a string to Query Object

$Id$
"""

#TODOs:
#add metadata into the picture!!!
#remove shift/reduce conflicts, when possible
#look after raise "Help"
#revise according to new grammar

from ply import lex, yacc
from collections import deque
from threading import local

from zope.component import adapts
from zope.component import provideAdapter
from zope.interface import implements

from ocql.queryobject.queryobject import *
from ocql.interfaces import IQueryParser

DEBUG = 0

class SymbolContainer:
    def __init__(self):
        self.stack = deque()
        self.stack.append(dict())

    def addlevel(self):
        top = self.current()
        new = dict(top)
        self.stack.append(new)

    def dellevel(self):
        self.stack.pop()

    def current(self):
        return self.stack[-1]

#further expand COND_OP, MODIFIER, QUANTOR
tokens = ('TYPE', 'UNION', 'DIFFER', 'AND', 'OR', 'NOT', 'ELLIPSIS', 'IN',
        'AS', 'SIZE', 'EQ','NE','LT','GT','LE','GE', 'ATLEAST','ATMOST','JUST','EVERY','SOME', 'CONSTANT',
        'IDENTIFIER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'BRACEL', 'BRACER',
        'SQUAREL', 'SQUARER', 'CURLYL', 'CURLYR',
        'PIPE', 'DOT', 'SEMICOL', 'COMMA'
        )

precedence = (
    ('left', 'UNION'),
    ('left', 'DIFFER'),
#   ('token', 'SQUAREL'),
#   ('token', 'PIPE'),
#   ('token', 'SQUARER'),
    ('left', 'AND'),
    ('left', 'OR'),
    ('right', 'NOT'),
    ('left', 'EQ'),
    ('left', 'NE'),
    ('left', 'LT'),
    ('left', 'GT'),
    ('left', 'LE'),
    ('left', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MUL', 'DIV'),
#   ('token', 'IDENTIFIER'),
#   ('token', 'BRACEL'),
#   ('token', 'BRACER'),
#   ('token', 'CONSTANT'),
#   ('token', 'TYPE'),
#   ('token', 'CURLYL'),
#   ('token', 'CURLYR'),
#   ('token', 'ELLIPSIS'),
    ('left', 'DOT'),
#   ('token', 'COMMA'),
    ('left', 'SEMICOL'),

    ('left', 'IN'),
    ('left', 'AS'),

#   ('token', 'MODIFIER'),
#   ('token', 'QUANTOR'),

    ('left', 'SIZE'),
)

class Lexer(object):
    tokens = tokens
    t_ignore = ' \t\n\r'

    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    # Tokens
    def t_TYPE(self, t):
        r'(set|bag|map|list)'
        return t

    def t_UNION(self, t):
        r'union'
        return t

    def t_DIFFER(self, t):
        r'differ'
        return t

    def t_AND(self, t):
        r'and'
        return t

    def t_OR(self, t):
        r'or'
        return t

    def t_NOT(self, t):
        r'not'
        return t

    def t_ELLIPSIS(self, t):
        r'\.\.\.'
        return t

    def t_IN(self, t):
        r'in'
        return t

    def t_AS(self, t):
        r'as'
        return t

    def t_SIZE(self, t):
        r'size'
        return t

    #def t_COND_OP(self, t):
    #    r'(<|>|<=|>=|==|!=)'
    #    return t

    def t_LT(self, t):
        r'<'
        return t
    
    def t_GT(self, t):
        r'>'
        return t
    
    def t_LE(self, t):
        r'<='
        return t
    
    def t_GE(self, t):
        r'>='
        return t
    
    def t_EQ(self, t):
        r'=='
        return t
    
    def t_NE(self, t):
        r'!='
        return t 
    
    #def t_MODIFIER(self, t):
    #    r'(atleast|atmost|just)'
    #    return t

    def t_ATLEAST(self, t):
        r'atleast'
        return t
    
    def t_ATMOST(self, t):
        r'atmost'
        return t
    
    def t_JUST(self, t):
        r'just'
        return t
    
    #def t_QUANTOR(self, t):
    #    r'(every|some)'
    #    return t

    def t_EVERY(self, t):
        r'every'
        return t
    
    def t_SOME(self, t):
        r'some'
        return t
    
    def t_CONSTANT(self, t):
        r'(\'(\\.|[^\'])*\'|"(\\.|[^"])*"|[0-9]+)'
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z][0-9a-zA-Z_]*'
        if DEBUG: print "IDEN", t
        return t

    def t_PLUS(self, t):
        r'\+'
        return t

    def t_MINUS(self, t):
        r'-'
        return t

    def t_MUL(self, t):
        r'\*'
        return t

    def t_DIV(self, t):
        r'/'
        return t

    def t_BRACEL(self, t):
        r'\('
        return t

    def t_BRACER(self, t):
        r'\)'
        return t

    def t_SQUAREL(self, t):
        r'\['
        return t

    def t_SQUARER(self, t):
        r'\]'
        return t

    def t_CURLYL(self, t):
        r'{'
        return t

    def t_CURLYR(self, t):
        r'}'
        return t

    def t_PIPE(self, t):
        r'\|'
        return t

    def t_DOT(self, t):
        r'\.'
        return t

    def t_SEMICOL(self, t):
        r';'
        return t

    def t_COMMA(self, t):
        r','
        return t

class Parser(object):
    tokens = tokens
    precedence = precedence
    metadata = None
    symbols = None
    types = { 'set' : set, 'list': list }
    start = 'expr'

    def __init__(self, metadata):
        self.metadata = metadata
        self.symbols = SymbolContainer()

    def p_error(self, t):
        print "Syntax error at '%s' (%s)" % (t.value, t.lexpos)

    #expr COND_OP modifier nexpr seems to be wrong logically
    #def p_expr_cond(self, t):
    #    r'''expr : modifier nexpr COND_OP modifier nexpr
    #             | modifier expr COND_OP modifier nexpr'''
    #    raise "Help"

    def p_expr_atleast(self, t):
        r'''expr : ATLEAST expr 
        '''
        t[0] = Atleast(self.metadata, self.symbols, t[2])
        
    def p_expr_atmost(self, t):
        r'''expr : ATMOST expr 
        '''
        t[0] = Atmost(self.metadata, self.symbols, t[2])
        
    def p_expr_just(self, t):
        r'''expr : JUST expr 
        '''
        t[0] = Just(self.metadata, self.symbols, t[2])

    def p_expr_every(self, t):
        r'''expr : EVERY expr 
        '''
        t[0] = Every(self.metadata, self.symbols, t[2])
                
    def p_expr_some(self, t):
        r'''quented : expr
                    | SOME expr 
        '''
        if len(t)==2:
            t[0] = t[1]
        else:
            t[0] = Some(self.metadata, self.symbols, t[2])
        
    def p_expr_eq(self, t):
        r'''expr : quented EQ expr
        '''
        t[0] = Eq(self.metadata, self.symbols, t[1], t[3])
        
    def p_expr_ne(self, t):
        r'''expr : expr NE expr
        '''
        t[0] = Ne(self.metadata, self.symbols, t[1], t[3])

    def p_expr_lt(self, t):
        r'''expr : expr LT expr
        '''
        t[0] = Lt(self.metadata, self.symbols, t[1], t[3])

    def p_expr_gt(self, t):
        r'''expr : expr GT expr
        '''
        t[0] = Gt(self.metadata, self.symbols, t[1], t[3])
        
    def p_expr_le(self, t):
        r'''expr : expr LE expr
        '''
        t[0] = Le(self.metadata, self.symbols, t[1], t[3])
        
    def p_expr_ge(self, t):
        r'''expr : expr GE expr
        '''
        t[0] = Ge(self.metadata, self.symbols, t[1], t[3])
        
    def p_expr_union(self, t):
        r'''expr : expr UNION expr
        '''
        t[0] = Union(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_differ(self, t):
        r'''expr : expr DIFFER expr
        '''
        t[0] = Differ(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_equery(self, t):
        r'''expr : TYPE SQUAREL xprs SQUARER
        '''
        #I also change the expected query in parser.txt
        t[0] = Query(self.metadata, self.symbols, self.types[t[1]],t[3],None)
        
    def p_expr_query(self, t):
        r'''expr : TYPE SQUAREL xprs PIPE expr SQUARER
        '''
        t[0] = Query(self.metadata, self.symbols, self.types[t[1]], t[3], t[5])
        if DEBUG: print "p_expr_query", t[0]

    def p_expr_and(self, t):
        r'''expr : expr AND expr
        '''
        t[0] = And(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_or(self, t):
        r'''expr : expr OR expr
        '''
        t[0] = Or(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_plus(self, t):
        r'''expr : expr PLUS expr
        '''
        t[0] = Add(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_minus(self, t):
        r'''expr : expr MINUS expr
        '''
        t[0] = Sub(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_mul(self, t):
        r'''expr : expr MUL expr
        '''
        t[0] = Mul(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_div(self, t):
        r'''expr : expr DIV expr
        '''
        t[0] = Div(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_not(self, t):
        r'''expr : NOT expr
        '''
        t[0] = Not(self.metadata, self.symbols, t[2])
        if DEBUG: print t[0]

    def p_expr_dot(self, t):
        r'''expr : expr DOT expr
        '''
        t[0] = Property(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print t[0]

    def p_expr_id(self, t):
        r'''expr : IDENTIFIER
        '''
        t[0] = Identifier(self.metadata, self.symbols, t[1])
        if DEBUG: print "p_expr_id", t[0]


    def p_expr_call(self, t):
        r'''expr : IDENTIFIER BRACEL exprs BRACER
        '''
        raise NotImplementedError("Function call")
    
    def p_expr_const(self, t):
        r'''expr : CONSTANT
        '''
        t[0] = Constant(self.metadata, self.symbols, t[1])
        if DEBUG: print t[0]

    def p_expr_array(self, t):
        r'''expr : TYPE '{' exprs '}'
        '''
        raise NotImplementedError("array")

    def p_expr_range(self, t):
        r'''expr : TYPE CURLYL expr ELLIPSIS expr CURLYR
        '''
        raise NotImplementedError("range")


    def p_expr_index(self, t):
        r'''expr : expr DOT SQUAREL expr SQUARER
        '''
        t[0] = Index(self.metadata, self.symbols, t[1], t[4])
        if DEBUG: print t[0]

    def p_expr_size(self, t):
        r'''expr : SIZE expr
        '''
        t[0] = Count(self.metadata, self.symbols, t[2])
        if DEBUG: print t[0]

    def p_expr_bracket(self, t):
        r'''expr : BRACEL expr BRACER
        '''
        t[0] = t[2]
        if DEBUG: print t[0]

    #def p_omodifier(self, t):
    #    r'''omodifier : QUANTOR
    #                  | MODIFIER
    #    '''
    #    if DEBUG: print t[0]

    #def p_modifier(self, t):
    #    r'''modifier : QUANTOR
    #                 | MODIFIER
    #    '''
    #    if DEBUG: print t[0]

    def p_exprs(self, t):
        r'''exprs : expr
                  | expr COMMA exprs
        '''
        if DEBUG: print t[0]

    def p_in_expr(self, t):
        r'''in_expr : IDENTIFIER IN expr'''
        t[0] = In(self.metadata,
                  self.symbols,
                  Identifier(self.metadata,
                             self.symbols,
                             t[1]),
                  t[3])
        if DEBUG: print "p_in_expr", t[0]
        if DEBUG: print t[1], t[3]

    def p_as_expr(self, t):
        r'''as_expr : IDENTIFIER AS expr'''
        if DEBUG: print "p_as_expr", t[0]

    def p_xprs(self, t):
        r'''xprs :
                 | xpr SEMICOL xprs
                 | xpr
        '''
        if len(t)==1:
            t[0] = []
        elif len(t)==2:
            t[0] = [ t[1] ]
        else:
            t[3].insert(0,t[1])
            t[0] = t[3]
        if DEBUG: print "p_xprs", t[0]

    def p_xpr(self, t):
        r'''xpr : as_expr
                | in_expr
                | expr
        '''
        t[0] = t[1]
        if DEBUG: print "p_xpr", t[0]

#these are here, to keep lexer and parser instantiation to a minimum possible
#level because they are quite expensive operations
#parsers must be thread safe on the other hand!
LEXER = lex.lex(object=Lexer(), debug=0)
#PARSERS = local()

def parse(str, metadata):
    lexer = LEXER.clone()

    #global PARSERS
    #try:
    #    parser = PARSERS.parser
    #
    #    try:
    #        parser.restart()
    #    except AttributeError:
    #        pass
    #
    #except AttributeError:
    #    parser = yacc.yacc(module = Parser(metadata))
    #    PARSERS.parser = parser

    try:
        parser = yacc.yacc(module = Parser(metadata))

        retval = parser.parse(str, lexer = lexer)
    except Exception, e:
        if DEBUG: print e
        raise
    return retval

class QueryParser(object):
    implements(IQueryParser)
    adapts(basestring)

    def __init__(self, context):
        self.context = context
        #self.db = db

    def __call__(self, metadata):
        strg = self.context
        tree = parse(strg, metadata)
        head = Head(tree)
        return head
        #return parse(strg, None)
