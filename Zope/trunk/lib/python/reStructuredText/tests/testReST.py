# -*- coding: iso-8859-15 -*-

import unittest

from reStructuredText import HTML


txt = """Hello World
============

text text

Von V�geln und �fen
===================

- some
- more
- text

"""


class TestReST(unittest.TestCase):

    def testRoman(self):
        # Make sure we can import the rst parser
        from docutils.parsers import rst

    def testEncodings(self):

        def _test(txt, in_enc, out_enc):
            return HTML(txt,
                        input_encoding=in_enc,
                        output_encoding=out_enc)

        encoding = 'iso-8859-15'
        html = _test(txt, encoding, encoding)
        self.assertEqual('V�gel' in html, True)
        self.assertEqual('�fen' in html, True)

        html = _test(txt, encoding, 'unicode')
        self.assertEqual(unicode('V�gel', encoding) in html, True)
        self.assertEqual(unicode('�fen', encoding) in html, True)

        html = _test(unicode(txt, encoding), 'unicode', encoding)
        self.assertEqual('V�gel' in html, True)
        self.assertEqual('�fen' in html, True)

        html = _test(unicode(txt, encoding), 'unicode', 'unicode')
        self.assertEqual(unicode('V�gel', encoding) in html, True)
        self.assertEqual(unicode('�fen', encoding) in html, True)

    def testHeaderLevel(self):

        encoding = 'iso-8859-15'
        for level in range(0, 5):
            html = HTML(txt, input_encoding=encoding, 
                             output_encoding=encoding, 
                             initial_header_level=level)
            self.assertEqual('<h%d><a name="hello-world">Hello World</a></h%d>'\
                              % (level+1, level+1) in html,
                             True)
            self.assertEqual('<h%d><a name="von-v-geln-und-fen">Von V�geln und �fen</a></h%d>'\
                              % (level+1, level+1) in html,
                             True)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    return TestSuite((makeSuite(TestReST),))

