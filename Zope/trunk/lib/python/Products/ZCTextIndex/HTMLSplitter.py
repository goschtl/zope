##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

import re

class HTMLWordSplitter:

    __implements__ = ISplitter

    def process(self, text, wordpat=r"\w+"):
        splat = []
        for t in text:
            splat += self._split(t, wordpat)
        return splat

    def processGlob(self, text):
        return self.process(text, r"\w+[\w*?]*") # see Lexicon.globToWordIds()

    def _split(self, text, wordpat):
        text = text.lower()
        remove = [r"<[^<>]*>",
                  r"&[A-Za-z]+;"]
        for pat in remove:
            text = re.sub(pat, " ", text)
        return re.findall(wordpat, text)

element_factory.registerFactory('Word Splitter',
                                'HTML aware splitter',
                                HTMLWordSplitter)

if __name__ == "__main__":
    import sys
    splitter = HTMLWordSplitter()
    for path in sys.argv[1:]:
        f = open(path, "rb")
        buf = f.read()
        f.close()
        print path
        print splitter.process([buf])
