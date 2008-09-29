import sys
import unittest
from chameleon.genshi.tests.test_doctests import render_template

class UnicodeTortureTests(unittest.TestCase):

    def test_torture(self):
        body = """\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:py="http://genshi.edgewall.org/">
        <title>\xc2\xa9</title>
        <div id="${foo}" py:attrs="dict(label=foo)"/>
        </html>
        """
        expected = """\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html>
        <title>\xc2\xa9</title>
        <div label="\xc2\xa9" id="\xc2\xa9"/>
        </html>"""

        c = unicode('\xc2\xa9', 'utf-8')
        self.assertEqual(render_template(body, foo=c), expected)

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

