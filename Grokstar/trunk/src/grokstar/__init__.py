# this directory is a package
from docutils import nodes
from docutils.parsers.rst import directives
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

pygments_formatter = HtmlFormatter()

def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except ValueError:
        # no lexer found - use the text one instead of an exception
        lexer = get_lexer_by_name('text')
    parsed = highlight(u'\n'.join(content), lexer, pygments_formatter)
    return [nodes.raw('', parsed, format='html')]
pygments_directive.arguments = (1, 0, 1)
pygments_directive.content = 1
directives.register_directive('sourcecode', pygments_directive)

from grok import View, Viewlet, Application
def application(self, name=None):
    obj = self.context
    while obj is not None:
        if isinstance(obj, Application):
            return obj
        obj = obj.__parent__
    raise ValueError("No application found.")


View.application = property(application)
Viewlet.application = property(application)
#XXX You didn't really see me do that, did you?