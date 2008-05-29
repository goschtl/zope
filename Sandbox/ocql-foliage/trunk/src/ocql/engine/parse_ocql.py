tokens = ('TYPE', 'UNION', 'DIFFER', 'AND', 'OR', 'NOT', 'ELLIPSIS', 'IN',
        'AS', 'SIZE', 'COND_OP', 'MODIFIER', 'QUANTOR', 'CONSTANT',
        'IDENTIFIER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'BRAL', 'BRAR',
        'SQL', 'SQR', 'CURL', 'CURR', 'PIPE', 'DOT', 'SEMICOL', 'COMMA'
        )

precedence = (
    ('left', 'UNION'),
    ('left', 'DIFFER'),
#   ('token', 'SQL'),
#   ('token', 'PIPE'),
#   ('token', 'SQR'),
    ('left', 'AND'),
    ('left', 'OR'),
    ('right', 'NOT'),
    ('left', 'COND_OP'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MUL', 'DIV'),
#   ('token', 'IDENTIFIER'),
#   ('token', 'BRAL'),
#   ('token', 'BRAR'),
#   ('token', 'CONSTANT'),
#   ('token', 'TYPE'),
#   ('token', 'CURL'),
#   ('token', 'CURR'),
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
        r'(set|bag|map)'
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

    def t_COND_OP(self, t):
        r'(<|>|<=|>=|==|!=)'
        return t

    def t_MODIFIER(self, t):
        r'(atleast|atmost|just)'
        return t

    def t_QUANTOR(self, t):
        r'(every|some)'
        return t

    def t_CONSTANT(self, t):
        r'(\'(\\.|[^\'])*\'|"(\\.|[^"])*"|[0-9]+)'
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z][0-9a-zA-Z_]*'
        print "IDEN", t
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

    def t_BRAL(self, t):
        r'\('
        return t

    def t_BRAR(self, t):
        r'\)'
        return t

    def t_SQL(self, t):
        r'\['
        return t

    def t_SQR(self, t):
        r'\]'
        return t

    def t_CURL(self, t):
        r'{'
        return t

    def t_CURR(self, t):
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

from ocql.engine.queryobject import *

class Parser(object):
    tokens = tokens
    precedence = precedence
    metadata = None
    types = { 'set' : set, 'list': list }
    start = 'expr'

    def __init__(self, metadata):
        self.metadata = metadata

    def p_error(self, t):
        print "Syntax error at '%s'" % t.value

    def p_expr_cond(self, t):
        r'''expr : modifier nexpr COND_OP omodifier nexpr
                 | expr COND_OP omodifier nexpr'''
        raise "Help"

    def p_expr_union(self, t):
        r'''expr : expr UNION expr
            nexpr : nexpr UNION nexpr
        '''
        t[0] = Union(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_differ(self, t):
        r'''expr : expr DIFFER expr
            nexpr : nexpr DIFFER nexpr
        '''
        t[0] = Differ(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_query(self, t):
        r'''expr : TYPE SQL xprs PIPE expr SQR
            nexpr : TYPE SQL xprs PIPE expr SQR
        '''
        t[0] = Query(self.metadata, self.types[t[1]], t[3], t[5])
        print "p_expr_query", t[0]

    def p_expr_and(self, t):
        r'''expr : expr AND expr
            nexpr : nexpr AND nexpr
        '''
        t[0] = And(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_or(self, t):
        r'''expr : expr OR expr
            nexpr : nexpr OR nexpr
        '''
        t[0] = Or(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_plus(self, t):
        r'''expr : expr PLUS expr
            nexpr : nexpr PLUS nexpr
        '''
        t[0] = Add(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_minus(self, t):
        r'''expr : expr MINUS expr
            nexpr : nexpr MINUS nexpr
        '''
        t[0] = Sub(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_mul(self, t):
        r'''expr : expr MUL expr
            nexpr : nexpr MUL nexpr
        '''
        t[0] = Mul(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_div(self, t):
        r'''expr : expr DIV expr
            nexpr : nexpr DIV nexpr
        '''
        t[0] = Div(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_not(self, t):
        r'''expr : NOT expr
            nexpr : NOT nexpr
        '''
        t[0] = Not(self.metadata, t[2])
        print t[0]

    def p_expr_dot(self, t):
        r'''expr : expr DOT expr
            nexpr : nexpr DOT expr
        '''
        t[0] = Property(self.metadata, t[1], t[3])
        print t[0]

    def p_expr_id(self, t):
        r'''expr : IDENTIFIER
           nexpr : IDENTIFIER
        '''
        t[0] = Identifier(self.metadata, t[1])
        print "p_expr_id", t[0]


    def p_expr_call(self, t):
        r'''expr : IDENTIFIER BRAL exprs BRAR
            nexpr : IDENTIFIER BRAL exprs BRAR
        '''
        raise "Not implemented: function call"

    def p_expr_const(self, t):
        r'''expr : CONSTANT
            nexpr : CONSTANT
        '''
        t[0] = Constant(self.metadata, t[1])
        print t[0]

    def p_expr_array(self, t):
        r'''expr : TYPE '{' exprs '}'
            nexpr : TYPE '{' exprs '}'
        '''
        raise "Not implemented: array"

    def p_expr_range(self, t):
        r'''expr : TYPE CURL expr ELLIPSIS expr CURR
            nexpr : TYPE CURL expr ELLIPSIS expr CURR
        '''
        raise "Not implemented: range"


    def p_expr_index(self, t):
        r'''expr : expr DOT SQL expr SQR
            nexpr : nexpr DOT SQL expr SQR
        '''
        t[0] = Index(self.metadata, t[1], t[4])
        print t[0]

    def p_expr_size(self, t):
        r'''expr : SIZE expr
            nexpr : SIZE expr
        '''
        t[0] = Count(self.metadata, t[2])
        print t[0]

    def p_expr_bracket(self, t):
        r'''expr : BRAL expr BRAR
            nexpr : BRAL expr BRAL
        '''
        t[0] = t[2]
        print t[0]

    def p_omodifier(self, t):
        r'''omodifier : QUANTOR
                      | MODIFIER
        '''
        print t[0]

    def p_modifier(self, t):
        r'''modifier : QUANTOR
                     | MODIFIER
        '''
        print t[0]

    def p_exprs(self, t):
        r'''exprs : expr
                  | expr COMMA exprs
        '''
        print t[0]

    def p_in_expr(self, t):
        r'''in_expr : IDENTIFIER IN expr'''
        t[0] = In(self.metadata, Identifier(self.metadata, t[1]), t[3])
        print "p_in_expr", t[0]
        print t[1], t[3]

    def p_as_expr(self, t):
        r'''as_expr : IDENTIFIER AS expr'''
        print "p_as_expr", t[0]

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
            t[3].insert(t[0], 0)
            t[0] = t[3]
        print "p_xprs", t[0]

    def p_xpr(self, t):
        r'''xpr : as_expr
                | in_expr
                | expr
        '''
        t[0] = t[1]
        print "p_xpr", t[0]

def parse(str, metadata):
    from ply import lex, yacc
    lexer = lex.lex(object=Lexer(), debug=0)
    parser = yacc.yacc(module = Parser(metadata))

    print str
    try:
        x= parser.parse(str, lexer = lexer)
        print x
    except Exception, e:
        print e
    return x
