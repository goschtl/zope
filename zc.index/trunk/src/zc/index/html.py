import re
import htmlentitydefs

import BeautifulSoup

from zc.index import text

unichr_entity = re.compile(r'\#(\d+)$')

class TextSoup(BeautifulSoup.BeautifulSoup):
    """Derived text extractor that includes less junk."""

    def handle_charref(self, codepoint):
        self.handle_data(unichr(int(codepoint)))

    def handle_comment(self, text):
        # discard text in HTML comments
        pass

    def handle_decl(self, text):
        # discard DOCTYPE and the like
        pass

    def handle_entityref(self, name):
        if name in htmlentitydefs.name2codepoint:
            self.handle_data(unichr(htmlentitydefs.name2codepoint[name]))
        else:
            match = unichr_entity.match(name)
            if match:
                self.handle_data(unichr(int(match.group(1))))
            else:
                BeautifulSoup.BeautifulSoup.handle_entityref(name)

    def handle_pi(self, text):
        # discard processing instructions
        pass

    def unknown_endtag(self, name):
        if name in ("script", "style"):
            self.currentData = []
        BeautifulSoup.BeautifulSoup.unknown_endtag(self, name)

class HTMLSearchableText(text.TextSearchableText):

    def getSearchableText(self):
        out = self.get_unicode()
        if out is not None:
            tree = TextSoup(out)
            res = []
            stack = [[iter((tree,)), False]]
            while stack:
                data = stack[-1]
                i, add_close_space = data
                try:
                    o = i.next()
                except StopIteration:
                    stack.pop()
                    if add_close_space:
                        res.append(' ')
                else:
                    add_close_space = False
                    if isinstance(o, BeautifulSoup.NavigableText):
                        res.append(o)
                        continue
                    elif isinstance(o, BeautifulSoup.Tag):
                        if (o.name=='input'
                            and o['type'] in (
                                'text', 'submit', 'reset', 'meta')):
                            v = o['value']
                            if v:
                                res.extend((' ', v, ' '))
                            continue
                        elif o.name=='img':
                            v = o['alt']
                            if v:
                                res.extend((' ', v, ' '))
                            continue
                        else:
                            if o.name in (
                                'style', 'script', 'applet', 'param', 'object',
                                'link', 'base', 'basefont', 'isindex'):
                                continue
                            elif o.name in (
                                'body', 'head', 'html', 'title', 'abbr',
                                'acronym', 'address', 'blockquote', 'br',
                                'cite', 'code', 'dfn', 'div', 'h1', 'h2',
                                'h3', 'h4', 'h5', 'h6', 'kbd', 'p', 'pre',
                                'q', 'samp', 'var', 'dl', 'dd', 'dt', 'ol',
                                'ul', 'li', 'hr', 'sub', 'sup', 'tt', 'form',
                                'input', 'label', 'select', 'option',
                                'textarea', 'button', 'legend', 'optgroup',
                                'fieldset', 'caption', 'table', 'td', 'th',
                                'tr', 'col', 'colgroup', 'tbody', 'thead',
                                'tfoot', 'area', 'map', 'frameset', 'frame',
                                'noframes', 'iframe', 'noscript', 'center',
                                'dir', 'menu'):
                                # not em, span, 'strong', 'a', 'b', 'big', 'i',
                                # 'small', 'del', 'ins', 'font', 's', 'strike',
                                # 'u'
                                res.append(' ')
                                add_close_space = True
                    stack.append([iter(o), add_close_space])
            res = ''.join(res).strip()
            if res:
                return (res,) # for interface
        return ()
