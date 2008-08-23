# -*- coding: UTF-8 -*-

"""Parse a string to Query Object

"""

#TODOs:
#remove shift/reduce conflicts, when possible
#look after raise "Help"
#parser caching does not work yet

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

tokens = ('SET', 'LIST', 'COMMA', 'NOT_EQUAL', 'UNION', 'AS', 'EVERY',
          'ATMOST', 'LT', 'GT', 'ELLIPSIS', 'BRACKET_R', 'OR', 'PIPE',
          'DOT', 'IN', 'LTE', 'SOME', 'AND', 'CBRACKET_L', 'CONSTANT',
          'EQUAL', 'GTE', 'ISINSTANCE', 'SEMI_COLON', 'BRACKET_L', 'ASSIGN',
          'NOT_ASSIGN', 'FOR', 'CBRACKET_R', 'JUST', 'IDENTIFIER', 'DIFFER',
          'LEN', 'BAG', 'SBRACKET_L', 'NOT', 'ATLEAST', 'SBRACKET_R', 
          'PLUS', 'MINUS', 'MUL', 'DIV')

precedence = (
    ('left', 'UNION'),
    ('left', 'DIFFER'),
#   ('token', 'SQUAREL'),
#   ('token', 'PIPE'),
#   ('token', 'SQUARER'),
    ('left', 'AND'),
    ('left', 'OR'),
    ('right', 'NOT'),
#   ('left', 'COND_OP'),
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
    ('left', 'SEMI_COLON'),

    ('left', 'IN'),
    ('left', 'AS'),

#   ('token', 'MODIFIER'),
#   ('token', 'QUANTOR'),

#    ('left', 'SIZE'),
)

class Lexer(object):
    tokens = tokens
    t_ignore = ' \t\n\r'

    def t_error(self, t):
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def t_UNION(self, t):
        r'union'
        return t

    def t_DIFFER(self, t):
        r'differ'
        return t

    def t_SET(self, t):
        r'set'
        return t

    def t_LIST(self, t):
        r'list'
        return t

    def t_BAG(self, t):
        r'bag'
        return t

    def t_FOR(self, t):
        r'for'
        return t

    def t_LEN(self, t):
        r'len'
        return t

    def t_AS(self, t):
        r'as'
        return t

    def t_IN(self, t):
        r'in'
        return t

    def t_OR(self, t):
        r'or'
        return t

    def t_AND(self, t):
        r'and'
        return t

    def t_NOT(self, t):
        r'not'
        return t

    def t_ISINSTANCE(self, t):
        r'isinstance'
        return t

    def t_EVERY(self, t):
        r'every'
        return t

    def t_ATMOST(self, t):
        r'atmost'
        return t

    def t_ATLEAST(self, t):
        r'atleast'
        return t

    def t_SOME(self, t):
        r'some'
        return t

    def t_JUST(self, t):
        r'just'
        return t

    def t_CONSTANT(self, t):
        r'(\'(\\.|[^\'])*\'|"(\\.|[^"])*"|[0-9]+)'
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z][0-9a-zA-Z_]*'
        return t

    def t_COMMA(self, t):
        r','
        return t

    def t_NOT_EQUAL(self, t):
        r'!='
        return t

    def t_LTE(self, t):
        r'<='
        return t

    def t_LT(self, t):
        r'<'
        return t

    def t_GTE(self, t):
        r'>='
        return t

    def t_GT(self, t):
        r'>'
        return t

    def t_ELLIPSIS(self, t):
        r'\.\.\.'
        return t

    def t_PIPE(self, t):
        r'\|'
        return t

    def t_DOT(self, t):
        r'\.'
        return t

    def t_MUL(self, t):
        r'\*'
        return t

    def t_CBRACKET_L(self, t):
        r'{'
        return t

    def t_CBRACKET_R(self, t):
        r'}'
        return t

    def t_EQUAL(self, t):
        r'=='
        return t

    def t_SEMI_COLON(self, t):
        r';'
        return t

    def t_BRACKET_L(self, t):
        r'\('
        return t

    def t_BRACKET_R(self, t):
        r'\)'
        return t

    def t_ASSIGN(self, t):
        r'='
        return t

    def t_NOT_ASSIGN(self, t):
        r'~='
        return t

    def t_PLUS(self, t):
        r'\+'
        return t

    def t_MINUS(self, t):
        r'-'
        return t

    def t_DIV(self, t):
        r'/'
        return t

    def t_SBRACKET_L(self, t):
        r'\['
        return t

    def t_SBRACKET_R(self, t):
        r'\]'
        return t



class Parser(object):
    tokens = tokens
    precedence = precedence
    metadata = None
    symbols = None
    types = { 'set' : set, 'list': list }
    start = 'expression'

    def __init__(self, metadata):
        self.metadata = metadata
        self.symbols = SymbolContainer()

    def p_error(self, t):
        print "Syntax error at '%s' (%s)" % (t.value, t.lexpos)

    def p_expr_union(self, t):
        r'''expression : expression UNION expression
        '''
        t[0] = Union(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "expression UNION expression" to "expression"', t[0]

    def p_expr_differ(self, t):
        r'''expression : expression DIFFER expression
        '''
        t[0] = Differ(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "expression DIFFER expression" to "expression"', t[0]

    def p_expr_plus(self, t):
        r'''expression : expression PLUS expression
        '''
        t[0] = Add(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "expression UNION expression" to "expression"', t[0]

    def p_expr_minus(self, t):
        r'''expression : expression MINUS expression
        '''
        t[0] = Sub(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "expression UNION expression" to "expression"', t[0]

    def p_expr_mul(self, t):
        r'''expression : expression MUL expression
        '''
        t[0] = Mul(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "expression UNION expression" to "expression"', t[0]

    def p_expr_div(self, t):
        r'''expression : expression DIV expression
        '''
        t[0] = Div(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "expression UNION expression" to "expression"', t[0]

#    def p_expr_3(self, t):
#        r'''expression : collection SBRACKET_L expression SBRACKET_R
#        '''
#        t[0] = Query(self.metadata, self.symbols, t[1], [], t[3])
#        if DEBUG: print 'reducing "collection SBRACKET_L qualifier PIPE expression SBRACKET_R" to "expression"'

    def p_expr_query(self, t):
        r'''expression : collection SBRACKET_L qualifier PIPE expression SBRACKET_R
        '''
        t[0] = Query(self.metadata, self.symbols, t[1], t[3], t[5])
        if DEBUG: print 'reducing "collection SBRACKET_L qualifier PIPE expression SBRACKET_R" to "expression"', t[0]

#TODO add a test
    def p_expr_for_query(self, t):
        r'''expression : collection SBRACKET_L expression FOR qualifier  SBRACKET_R
        '''
        t[0] = Query(self.metadata, self.symbols, t[1], t[5], t[3])
        if DEBUG: print 'reducing "collection SBRACKET_L qualifier FOR expression SBRACKET_R" to "expression"', t[0]

    def p_expr_literal(self, t):
        r'''expression : literal
        '''
        t[0] = t[1]
        if DEBUG: print 'reducing "literal" to "expression"', t[0]

    def p_expr_path(self, t):
        r'''expression : path
        '''
        t[0] = t[1]
        if DEBUG: print 'reducing "path" to "expression"', t[0]

    def p_expr_call(self, t):
        r'''expression : call
        '''
        t[0] = t[1]
        if DEBUG: print 'reducing "path" to "expression"', t[0]

    def p_expr_len(self, t):
        r'''expression : LEN BRACKET_L expression BRACKET_R
        '''
        t[0] = Count(self.metadata, self.symbols, t[3])
        if DEBUG: print 'reducing "LEN BRACKET_L expression BRACKET_R" to "expression"', t[0]

    def p_collection_set(self, t):
        r'''collection : SET
        '''
        t[0] = self.types['set']
        if DEBUG: print 'reducing "set" to "collection"', t[0]

    def p_collection_list(self, t):
        r'''collection : LIST
        '''
        t[0] = self.types['list']
        if DEBUG: print 'reducing "list" to "collection"', t[0]

    def p_collection_bag(self, t):
        r'''collection : BAG
        '''
        raise NotImplementedError('bag')
        if DEBUG: print 'reducing "bag" to "collection"', t[0]

    def p_qualifier_null(self, t):
        r'''qualifier :
        '''
        t[0] = []
        if DEBUG: print 'reducing "" to "qualifier"', t[0]

    def p_qualifier_generator(self, t):
        r'''qualifier : generator
        '''
        t[0] = [t[1]]
        if DEBUG: print 'reducing "generator" to "qualifier"', t[0]

    def p_qualifier_definition(self, t):
        r'''qualifier : definition
        '''
        t[0] = [t[1]]
        if DEBUG: print 'reducing "definition" to "qualifier"', t[0]

    def p_qualifier_filter(self, t):
        r'''qualifier : filter
        '''
        t[0] = [t[1]]
        if DEBUG: print 'reducing "filter" to "qualifier"', t[0]

    def p_qualifier_qualifier(self, t):
        r'''qualifier : qualifier SEMI_COLON qualifier
        '''
        if t[0]:
            t[0].extend(t[1])
            t[0].extend(t[3])
        else:
            t[0] = t[1]
            t[0].extend(t[3])

        if DEBUG: print 'reducing "qualifier SEMI_COLON qualifier" to "qualifier"', t[0]

#    def p_qualifier_6(self, t):
#        r'''qualifier : expression
#        '''
#        t[0] = t[1]
#        if DEBUG: print 'reducing "expression" to "qualifier"'

    def p_generator_in(self, t):
        r'''generator : IDENTIFIER IN expression
        '''
        t[0] = In(self.metadata,
                  self.symbols,
                  Identifier(self.metadata,
                             self.symbols,
                             t[1]),
                  t[3])
        if DEBUG: print 'reducing "IDENTIFIER IN expression" to "generator"', t[0]

    def p_filter_and(self, t):
        r'''filter : filter AND filter
        '''
        t[0] = And(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "filter AND filter" to "filter"', t[0]

    def p_filter_or(self, t):
        r'''filter : filter OR filter
        '''
        t[0] = Or(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "filter OR filter" to "filter"', t[0]

    def p_filter_not(self, t):
        r'''filter : NOT condition
        '''
        t[0] = Not(self.metadata, self.symbols, t[2])
        if DEBUG: print 'reducing "NOT condition" to "filter"', t[0]

    def p_filter_condition(self, t):
        r'''filter : condition
        '''
        t[0] = t[1]
        if DEBUG: print 'reducing "condition" to "filter"', t[0]

    def p_condition_filter(self, t):
        r'''condition : BRACKET_L filter BRACKET_R
        '''
        t[0] = t[2]
        if DEBUG: print 'reducing "BRACKET_L filter BRACKET_R" to "condition"', t[0]

    def p_condition_assign(self, t):
        r'''condition : quantified ASSIGN quantified
        '''
        raise NotImplementedError('assign')
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    def p_condition_not_assign(self, t):
        r'''condition : quantified NOT_ASSIGN quantified
        '''
        raise NotImplementedError('not assign')
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    def p_condition_lt(self, t):
        r'''condition : quantified LT quantified
        '''
        t[0] = Lt(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    def p_condition_lte(self, t):
        r'''condition : quantified LTE quantified
        '''
        t[0] = Le(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    def p_condition_gt(self, t):
        r'''condition : quantified GT quantified
        '''
        t[0] = Gt(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    def p_condition_gte(self, t):
        r'''condition : quantified GTE quantified
        '''
        t[0] = Ge(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    def p_condition_equal(self, t):
        r'''condition : quantified EQUAL quantified
        '''
        t[0] = Eq(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    def p_condition_not_equal(self, t):
        r'''condition : quantified  NOT_EQUAL quantified
        '''
        t[0] = Ne(self.metadata, self.symbols, t[1], t[3])
        if DEBUG: print 'reducing "quantified operator quantified" to "condition"', t[0]

    #need to extend this for collection of types
    def p_condition_isinstance(self, t):
        r'''condition : ISINSTANCE BRACKET_L expression COMMA IDENTIFIER BRACKET_R
        '''
        t[0] = Isinstance(self.metadata, self.symbols, t[3], t[5])
        if DEBUG: print 'reducing "ISINSTANCE BRACKET_L expression COMMA IDENTIFIER BRACKET_R" to "condition"', t[0]

    def p_quantified_expression(self, t):
        r'''quantified : expression
        '''
        t[0] = t[1]
        if DEBUG: print 'reducing "expression" to "quantified"', t[0]

    def p_quantified_some(self, t):
        r'''quantified : SOME expression
        '''
        t[0] = Some(self.metadata, self.symbols, t[2])
        if DEBUG: print 'reducing "quantification expression" to "quantified"', t[0]

    def p_quantified_every(self, t):
        r'''quantified : EVERY expression
        '''
        t[0] = Every(self.metadata, self.symbols, t[2])
        if DEBUG: print 'reducing "quantification expression" to "quantified"', t[0]

    def p_quantified_atleast(self, t):
        r'''quantified : ATLEAST CONSTANT expression
        '''
        t[0] = Atleast(self.metadata, self.symbols, t[2], t[3])
        if DEBUG: print 'reducing "quantification expression" to "quantified"', t[0]

    def p_quantified_almost(self, t):
        r'''quantified : ATMOST CONSTANT expression
        '''
        t[0] = Atmost(self.metadata, self.symbols, t[2], t[3])
        if DEBUG: print 'reducing "quantification expression" to "quantified"', t[0]

    def p_quantified_just(self, t):
        r'''quantified : JUST CONSTANT expression
        '''
        t[0] = Just(self.metadata, self.symbols, t[2], t[3])
        if DEBUG: print 'reducing "quantification expression" to "quantified"', t[0]

    def p_definition_as(self, t):
        r'''definition : IDENTIFIER AS expression
        '''
        t[0] = Alias(self.metadata, self.symbols,
                     Identifier(self.metadata, self.symbols, t[1]),
                     t[3])
        if DEBUG: print 'reducing "IDENTIFIER AS expression" to "definition"', t[0]

    def p_literal_constant(self, t):
        r'''literal : CONSTANT
        '''
        t[0] = Constant(self.metadata, self.symbols, t[1])
        if DEBUG: print 'reducing "CONSTANT" to "literal"', t[0]

    def p_literal_element(self, t):
        r'''literal : collection CBRACKET_L element CBRACKET_R
        '''
        raise NotImplementedError('collection set')
        if DEBUG: print 'reducing "collection CBRACKET_L element CBRACKET_R" to "literal"', t[0]

    def p_element_null(self, t):
        r'''element :
        '''
        t[0] = None
        if DEBUG: print 'reducing "" to "element"', t[0]

    def p_element_expression(self, t):
        r'''element : expression
        '''
        t[0] = t[1]
        if DEBUG: print 'reducing "expression" to "element"', t[0]

# Why this raise a shift/reduce conflict
#    def p_element_comma(self, t):
#        r'''element : element COMMA element
#        '''
#        raise NotImplementedError('element list')
#        if DEBUG: print 'reducing "element COMMA element" to "element"', t[0]

    def p_element_ellipsis(self, t):
        r'''element : expression ELLIPSIS expression
        '''
        raise NotImplementedError('range')
        if DEBUG: print 'reducing "expression ELLIPSIS expression" to "element"', t[0]

    def p_path_identifier(self, t):
        r'''path : IDENTIFIER
        '''
        t[0] = Identifier(self.metadata, self.symbols, t[1])
        if DEBUG: print 'reducing "IDENTIFIER" to "path"', t[0]

    def p_path_method(self, t):
        r'''method : IDENTIFIER DOT method
        '''
        t[0] = Property(self.metadata, self.symbols, Identifier(self.metadata, self.symbols, t[1]), t[3])
        if DEBUG: print 'reducing "IDENTIFIER DOT method" to "path"', t[0]

    def p_path_method2(self, t):
        r'''path : IDENTIFIER DOT method
        '''
        t[0] = Property(self.metadata, self.symbols, Identifier(self.metadata, self.symbols, t[1]), t[3])
        if DEBUG: print 'reducing "IDENTIFIER DOT method" to "path"', t[0]

    def p_method_identifier(self, t):
        r'''method : IDENTIFIER
        '''
        t[0] = Identifier(self.metadata, self.symbols, t[1])
        if DEBUG: print 'reducing "IDENTIFIER" to "method"', t[0]

    def p_method_arguments(self, t):
        r'''method : IDENTIFIER BRACKET_L argument_list BRACKET_R
        '''
        raise NotImplementedError('function call')
        if DEBUG: print 'reducing "IDENTIFIER BRACKET_L argument_list BRACKET_R" to "method"', t[0]

    def p_argument_list_null(self, t):
        r'''argument_list :
        '''
        t[0] = None
        if DEBUG: print 'reducing "" to "argument_list"', t[0]

    def p_argument_list_expression(self, t):
        r'''argument_list : expression
        '''
        t[0] = t[1]
        if DEBUG: print 'reducing "expression" to "argument_list"', t[0]

    def p_argument_list_set(self, t):
        r'''argument_list : expression COMMA argument_list
        '''
        t[0]=''
        if DEBUG: print 'reducing "expression COMMA argument_list" to "argument_list"', t[0]

    def p_call(self, t):
        r'''call : IDENTIFIER BRACKET_L argument_list BRACKET_R
        '''
        raise NotImplementedError('function call')
        if DEBUG: print 'reducing "IDENTIFIER BRACKET_L argument_list BRACKET_R" to "call"', t[0]

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
        return Head(tree)