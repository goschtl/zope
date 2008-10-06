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
        expected = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <title>\xc2\xa9</title>
        <div label="\xc2\xa9" id="\xc2\xa9"/>
        </html>"""
        c = unicode('\xc2\xa9', 'utf-8')
        result = render_template(body, foo=c).encode('utf-8')
        self.assertEqual(norm(result), norm(expected))

class WeirdoForms(unittest.TestCase):
    def test_lots_of_options(self):
        option = """<option value="one" py:attrs="dict(selected=value=='one' and 'yes' or None)">one</option>\n"""
        select = """<select py:with="value='one'">%s</select>\n""" % (70*option)

        body = """\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:xi="http://www.w3.org/2001/XInclude"
        xmlns:py="http://genshi.edgewall.org/">
        %s
        </html>
        """ % (20*select)
        result = render_template(body)

def norm(s):
    s = s.replace(' ', '')
    s = s.replace('\n', '')
    return s

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

