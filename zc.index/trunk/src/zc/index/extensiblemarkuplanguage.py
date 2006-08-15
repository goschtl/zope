# module is not called xml because of python relative import masking
# xml in standard library. :-/

import re
import htmlentitydefs

import BeautifulSoup

from zc.index import text

unichr_entity = re.compile(r'\#(\d+)$')

class TextSoup(BeautifulSoup.BeautifulStoneSoup):
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
            # I argue that these are common enough to use even for non-HTML XML
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

class XMLSearchableText(text.TextSearchableText):

    def getSearchableText(self):
        out = self.get_unicode()
        if out is not None:
            tree = TextSoup(out)
            textnodes = tree.fetchText(lambda *args: True,
                                       recursive=True)
            # we're going to guess that most tags divide words.  Just a guess.
            res = u" ".join(textnodes).strip()
            if res:
                return (res,) # for interface
        return ()
