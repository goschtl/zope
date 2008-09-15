import unittest

from zope.component.testing import PlacelessSetup

class TestNumericEntityPlusUnicodeParameterInsertedLiterally(unittest.TestCase,
                                                             PlacelessSetup):
    # See also
    # http://groups.google.com/group/z3c_pt/browse_thread/thread/aea963d25a1778d0?hl=en
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)
            
    def test_it(self):
        import chameleon.core
        from chameleon.core.testing import MockTemplate
        body = u"""\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        ${foo} &#169;
        </html>
        """
        expected = u"""\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        foo \xa9
        </html>"""
        t = MockTemplate(body)
        self.assertEqual(norm(t.render(foo=u'foo')), norm(expected))

class TestExplicitDoctypes(unittest.TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)

    def tearDown(self):
        PlacelessSetup.tearDown(self)

    def test_doctype_declared_in_constructor_adds_doctype(self):
        import chameleon.core
        from chameleon.core.testing import MockTemplate
        from chameleon.core import doctypes
        body = u"""\
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>
        """
        expected = u"""\
        <!DOCTYPE html PUBLIC"-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>"""
        t = MockTemplate(body, doctype=doctypes.xhtml_strict)
        self.assertEqual(norm(t.render()), norm(expected))

    def test_doctype_declared_in_constructor_overrides_template_doctype(self):
        import chameleon.core
        from chameleon.core.testing import MockTemplate
        from chameleon.core import doctypes
        body = u"""\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>
        """
        expected = u"""\
        <!DOCTYPE html PUBLIC"-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>"""
        t = MockTemplate(body, doctype=doctypes.xhtml_strict)
        self.assertEqual(norm(t.render()), norm(expected))

    def test_doctype_assigned_to_instance_overrides_constructor_doctype(self):
        import chameleon.core
        from chameleon.core.testing import MockTemplate
        from chameleon.core import doctypes
        body = u"""\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>
        """
        expected = u"""\
        <!DOCTYPE HTML PUBLIC"-//W3C//DTD HTML4.01 Transitional//EN"
        "http://www.w3.org/TR/html4/loose.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>"""
        t = MockTemplate(body, doctype=doctypes.html)
        t.doctype = doctypes.html
        self.assertEqual(norm(t.render()), norm(expected))

    def test_no_doctype_overrides_parsed_doctype(self):
        import chameleon.core
        from chameleon.core.testing import MockTemplate
        from chameleon.core import doctypes
        body = u"""\
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>
        """
        expected = u"""\
        <html xmlns="http://www.w3.org/1999/xhtml">
        </html>"""
        t = MockTemplate(body, doctype=doctypes.no_doctype)
        self.assertEqual(norm(t.render()), norm(expected))

def norm(s):
    return s.replace(' ', '').replace('\n', '')

def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])
