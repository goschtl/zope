from docutils import nodes
from docutils import utils

class ReST:

    element_types = {
        '#text': '_text',
        'StructuredTextDocument': 'document',
        'StructuredTextParagraph': 'paragraph',
        'StructuredTextExample': 'example',
        'StructuredTextBullet': 'bullet',
        'StructuredTextNumbered': 'numbered',
        'StructuredTextDescription': 'description',
        'StructuredTextDescriptionTitle': 'descriptionTitle',
        'StructuredTextDescriptionBody': 'descriptionBody',
        'StructuredTextSection': 'section',
        'StructuredTextSectionTitle': 'sectionTitle',
        'StructuredTextLiteral': 'literal',
        'StructuredTextEmphasis': 'emphasis',
        'StructuredTextStrong': 'strong',
        'StructuredTextLink': 'link',
        'StructuredTextXref': 'xref',
        'StructuredTextInnerLink':'innerLink',
        'StructuredTextNamedLink':'namedLink',
        'StructuredTextUnderline':'underline',
        'StructuredTextTable':'table',
        'StructuredTextSGML':'sgml',
        'StructuredTextImage': 'image',
        }

    LEVEL_MARKERS = ('#', '=', '+', '~', '-')

    def dispatch(self, doc, level, output):
        getattr(self, self.element_types[doc.getNodeName()]
               )(doc, level, output)

    def __call__(self, doc, level=1):
        r=[]
        self.dispatch(doc, level-1, r.append)
        return ''.join(r)

    def _text(self, doc, level, output):
        output(doc.getNodeValue())

    def document(self, doc, level, output):
        children = doc.getChildNodes()

        for c in children:
            self.dispatch(c, level, output)

    def section(self, doc, level, output):
        children=doc.getChildNodes()
        for c in children:
            self.dispatch(c, level + 1, output)

    def sectionTitle(self, doc, level, output):
        tmp = []
        for c in doc.getChildNodes():
            self.dispatch(c, level, tmp.append)
        header = ''.join(tmp).strip()
        divider = self.LEVEL_MARKERS[level - 1]
        output('%s\n' % header)
        output(divider * len(header))
        output('\n\n')

    def description(self, doc, level, output):
        p = doc.getPreviousSibling()
        if p is None or  p.getNodeName() is not doc.getNodeName():
            output('.. comment:: description list\n')
        output('\n')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        n=doc.getNextSibling()
        if n is None or n.getNodeName() is not doc.getNodeName():
            output('\n\n')

    def descriptionTitle(self, doc, level, output):
        for c in doc.getChildNodes():
            self.dispatch(c, level, output)

    def descriptionBody(self, doc, level, output):
        tmp = []
        for c in doc.getChildNodes():
            self.dispatch(c, level, tmp.append)
        output('\n  '.join(tmp))
        output('\n')

    def bullet(self, doc, level, output):
        p = doc.getPreviousSibling()
        if p is None or  p.getNodeName() is not doc.getNodeName():
            output('.. comment:: bullet list\n')
        output('\n')
        for c in doc.getChildNodes():
            output('- ')
            self.dispatch(c, level, output)
        n = doc.getNextSibling()
        if n is None or n.getNodeName() is not doc.getNodeName():
            output('\n\n')

    def numbered(self, doc, level, output):
        p = doc.getPreviousSibling()
        if p is None or  p.getNodeName() is not doc.getNodeName():
            output('.. comment:: numbered list\n')
        output('\n')
        for c in doc.getChildNodes():
            output('#. ')
            self.dispatch(c, level, output)
        n=doc.getNextSibling()
        if n is None or n.getNodeName() is not doc.getNodeName():
            output('\n\n')

    def example(self, doc, level, output):
        output('::\n\n')
        for c in doc.getChildNodes():
            output(c.getNodeValue())
        output('\n\n')

    def paragraph(self, doc, level, output):
        tmp = []
        for c in doc.getChildNodes():
            self.dispatch(c, level, tmp.append)
        para = ''.join(tmp)
        for line in para.splitlines():
            output('%s\n' % line.lstrip())
        output('\n\n')

    def link(self, doc, level, output):
        output('`')
        for c in doc.getChildNodes():
            self.dispatch(c, level, output)
        output(' <%s>`_' % doc.href)

    def emphasis(self, doc, level, output):
        output('*')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output('*>')

    def literal(self, doc, level, output):
        output(':: \n\n')
        for c in doc.getChildNodes():
            output(c.getNodeValue())
        output('\n\n')

    def strong(self, doc, level, output):
        output('**')
        for c in doc.getChildNodes():
            self.dispatch(c, level, output)
        output('**')

    def underline(self, doc, level, output):
        output("_")
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output("_")

    def innerLink(self, doc, level, output):
        assert 0 # TBD
        output('<a href="#ref');
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output('">[')
        for c in doc.getChildNodes():
            getattr(self, self.element_types[c.getNodeName()])(c, level, output)
        output(']</a>')

    def namedLink(self, doc, level, output):
        assert 0 # TBD
        output('<a name="ref')
        for c in doc.getChildNodes():
            self.dispatch(c, level, output)
        output('">[')
        for c in doc.getChildNodes():
            self.dispatch(c, level, output)
        output(']</a>')

    def sgml(self,doc,level,output):
        assert 0 # TBD
        for c in doc.getChildNodes():
            self.dispatch(c, level, output)

    def xref(self, doc, level, output):
        assert 0 # TBD
        val = doc.getNodeValue()
        output('<a href="#ref%s">[%s]</a>' % (val, val) )

    def table(self,doc,level,output):
        """
        A StructuredTextTable holds StructuredTextRow(s) which
        holds StructuredTextColumn(s). A StructuredTextColumn
        is a type of StructuredTextParagraph and thus holds
        the actual data.
        """
        assert 0 # TBD
        output('<table border="1" cellpadding="2">\n')
        for row in doc.getRows()[0]:
            output("<tr>\n")
            for column in row.getColumns()[0]:
                if hasattr(column,"getAlign"):
                    str = ('<%s colspan="%s" align="%s" valign="%s">'
                            % (column.getType(),
                               column.getSpan(),
                               column.getAlign(),
                               column.getValign()))
                else:
                    str = '<td colspan="%s">' % column.getSpan()
                output(str)
                for c in column.getChildNodes():
                    getattr(self, self.element_types[c.getNodeName()]
                                                 )(c, level, output)
                if hasattr(column,"getType"):
                    output("</"+column.getType()+">\n")
                else:
                    output("</td>\n")
            output("</tr>\n")
        output("</table>\n")

    def image(self, doc, level, output):
        assert 0 # TBD
        if hasattr(doc, 'key'):
            output('<a name="%s"></a>\n' % doc.key)
        output('<img src="%s" alt="%s" />\n' % (doc.href, doc.getNodeValue()))
        if doc.getNodeValue() and hasattr(doc, 'key'):
            output('<p><b>Figure %s</b> %s</p>\n' % (doc.key,
                                                     doc.getNodeValue()))

def restify(stxdoc):
    rest = ReST()
    return rest(stxdoc)
