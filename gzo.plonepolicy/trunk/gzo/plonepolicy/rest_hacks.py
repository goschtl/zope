"""
Define and register a code-block directive using pygments.

Define and register a sidebar directive.
"""

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.body import topic

import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import _get_ttype_class

#
# code-block directive
#

unstyled_tokens = ['']

class DocutilsInterface(object):
    """Parse `code` string and yield "classified" tokens.
    
    Arguments
    
      code     -- string of source code to parse
      language -- formal language the code is written in.
    
    Merge subsequent tokens of the same token-type. 
    
    Yields the tokens as ``(ttype_class, value)`` tuples, 
    where ttype_class is taken from pygments.token.STANDARD_TYPES and 
    corresponds to the class argument used in pygments html output.

    """

    def __init__(self, code, language):
        self.code = code
        self.language = language
        
    def lex(self):
        # Get lexer for language (use text as fallback)
        try:
            lexer = get_lexer_by_name(self.language)
        except ValueError:
            # info: "no pygments lexer for %s, using 'text'"%self.language
            lexer = get_lexer_by_name('text')
        return pygments.lex(self.code, lexer)
        
            
    def join(self, tokens):
        """join subsequent tokens of same token-type
        """
        tokens = iter(tokens)
        (lasttype, lastval) = tokens.next()
        for ttype, value in tokens:
            if ttype is lasttype:
                lastval += value
            else:
                yield(lasttype, lastval)
                (lasttype, lastval) = (ttype, value)
        yield(lasttype, lastval)

    def __iter__(self):
        """parse code string and yield "clasified" tokens
        """
        try:
            tokens = self.lex()
        except IOError:
            print "INFO: Pygments lexer not found, using fallback"
            # TODO: write message to INFO 
            yield ('', self.code)
            return

        for ttype, value in self.join(tokens):
            yield (_get_ttype_class(ttype), value)



def code_block_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    """parse and classify content of a code_block
    """
    language = arguments[0]
    
    # create a literal block element and set class argument
    code_block = nodes.literal_block(classes=["code-block", language])
    
    # parse content with pygments and add to code_block element
    for cls, value in DocutilsInterface(u'\n'.join(content), language):
        if cls in unstyled_tokens:
            # insert as Text to decrease the verbosity of the output.
            code_block += nodes.Text(value, value)
        else:
            code_block += nodes.inline(value, value, classes=[cls])

    return [code_block]


code_block_directive.arguments = (1, 0, 1)
code_block_directive.content = 1
directives.register_directive('code-block', code_block_directive)


#
# Sidebar directive
#

def sidebar(name, arguments, options, content, lineno,
                    content_offset, block_text, state, state_machine):
    if isinstance(state_machine.node, nodes.sidebar):
        error = state_machine.reporter.error(
                'The "%s" directive may not be used within a sidebar element.'
                % name, nodes.literal_block(block_text, block_text), line=lineno)
        return [error]
    return topic(name, arguments, options, content, lineno,
                    content_offset, block_text, state, state_machine,
                    node_class=nodes.sidebar)

sidebar.arguments = (1, 0, 1)
sidebar.options = {'subtitle': directives.unchanged_required,
    'class': directives.class_option}
sidebar.content = 1

directives.register_directive('sidebar', sidebar)
