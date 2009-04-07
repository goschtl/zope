"""Convert ZConfig configurations/files to ConfigParser style.
"""
import re
import cStringIO as StringIO
from ZConfigParser import schemaless, loadSchema
from xml.dom.minidom import parse, parseString

def convertFile(filepath):
    converter = ZConfConverter()
    return converter.convertFile(filepath)

class ZConfConverter(object):
    """Converter that turns ZConfig files into ZConfigParser configs.
    """

    defines = ''

    def convertFile(self, filepath):
        content = self.preprocess(open(filepath, 'rb').read())
        tree = parseString(content)
        defines, text = self.convertNode(tree.childNodes[0])
        return self.postprocess(defines, text)
        
    
    def preprocess(self, content):
        # We need some encapsulating tag to get a complete tree.
        content = '<zope>%s</zope>' % content
    
        # Replace 'invalid' tags like <server HTTP0> by valid tags,
        # <server name='HTTP0'>. Otherwise the minidom parser will
        # refuse our config.
        content = re.sub('<([^ >]+) ([^>]+)>', '<\\1 name="\\2">', content)
        return content

    def postprocess(self, defines, text):
        if len(defines):
            return '[DEFAULT]\n%s\n[zope]\n%s' % (defines, text)
        return '[zope]\n%s' % (text)

    def convertNode(self, node, prefix='zope'):
        body = ""
        subsections = ""
        defines = ""
        references = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE:
                new_defines, text = self.handleTextNode(child)
                body += text
                defines += new_defines
                continue
        
            # Get a unique subsection name if several with the same name
            # occur in the same section.
            num = 0
            child_name = child.nodeName
            child_is_list_item = False
            while child_name in references:
                child_is_list_item = True
                num += 1
                child_name = '%s.%s' % (child.nodeName, num)
            references.append(child_name)
        
            child_prefix = '%s/%s' % (prefix, child_name)
            if not child_is_list_item:
                body += '%s = %s\n' % (child_name, child_prefix)
            else:
                body += '%s%s\n' % (' '*(len(child.nodeName) + 3),
                                    child_prefix)

            subsections += "\n[%s]\n" % child_prefix
            if child.hasAttributes() and 'name' in child.attributes.keys():
                label = child.getAttribute('name').lower()
                subsections += "config-section-label = %s\n" % label
            new_defines, text = self.convertNode(child, prefix=child_prefix)
            subsections +=  text
            defines += new_defines
        return defines, body + subsections

    def handleTextNode(self, node):
        """Handle a text node.
        
        Text nodes may consist of several lines. Handle each separately.
        """
        text = node.data.strip()
        result = ""
        defines = ""
        if text == u'':
            return '', ''
        for line in text.split('\n'):
            new_defines, text = self.handleTextLine(line)
            defines += new_defines
            result += text
        return defines, result

    def handleTextLine(self, line):
        """Handle a text line.

        Replace defines, 
        """
        is_define = False
        line = line.strip()
        if line.startswith('%define'):
            line = re.sub('%define\s+([^\s+].+)', '\\1', line)
            is_define = True
        if line.startswith('#'):
            pass
        elif ' ' in line:
            line = re.sub('([^\s]+)\s+(.+)', '\\1 = \\2', line)
        line = re.sub('\$([A-Za-z0-9_]+)', '%(\\1)s', line)
        line += '\n'
        if is_define:
            return line, ''
        return '', line
