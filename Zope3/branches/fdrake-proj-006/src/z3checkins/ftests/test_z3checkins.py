#!/usr/bin/python
"""
Functional tests for z3checkins.

$Id: test_z3checkins.py,v 1.9 2004/05/15 13:23:59 gintautasm Exp $
"""

import unittest
import os
from zope.app.testing.functional import BrowserTestCase


class TestCheckins(BrowserTestCase):

    container_views = ('index.html', 'checkins-sidebar.html', 'checkins.rss')
    message_views = ('index.html', 'index.txt')
    resources = ('zope3.png', 'product.png', 'branch.png', 'message.png')

    def open(self, filename):
        """Open a file relative to the location of this module."""
        base = os.path.dirname(__file__)
        return open(os.path.join(base, filename))

    def setUp(self):
        BrowserTestCase.setUp(self)
        response = self.publish('/+/action.html', basic='mgr:mgrpw',
                form={'type_name': u'CheckinFolder', 'id': u'z3c'})
        self.assertEqual(response.getStatus(), 302)

        response = self.publish(
            '/+/CheckinFolder=z3c',
            basic='mgr:mgrpw',
            form={'field.description': u'Some description',
                  'field.archive_url': u'http://void',
                  'field.icons': u'icon\nanother one',
                  'UPDATE_SUBMIT': 'Add'})
        self.assertEqual(response.getStatus(), 302)
        z3c = self.getRootFolder()['z3c']
        self.assertEqual(z3c.description, u'Some description')
        self.assertEqual(z3c.archive_url, u'http://void')
        self.assertEqual(z3c.icons, u'icon\nanother one')

    def test_empty(self):
        for view in self.container_views:
            response = self.publish('/z3c/@@%s' % view)
            self.assertEqual(response.getStatus(), 200)

    def test_resources(self):
        for resource in self.resources:
            response = self.publish('/z3c/++resource++%s' % resource)
            self.assertEqual(response.getStatus(), 200)

    def test_add_checkin_message(self):
        response = self.publish('/z3c/@@+',
                                basic='mgr:mgrpw',
                                form={'field.data': self.open('msg1.txt'),
                                      'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody().count("Checkin message"), 1)

        response = self.publish('/z3c/+/CheckinMessage',
                                basic='mgr:mgrpw',
                                form={'field.data': self.open('msg1.txt'),
                                      'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)

        for view in self.container_views:
            response = self.publish('/z3c/@@%s' % view)
            self.assertEqual(response.getStatus(), 200)
        for view in self.message_views:
            response = self.publish('/z3c/msg1@example.org/@@%s' % view)
            self.assertEqual(response.getStatus(), 200)

        response = self.publish('/z3c/@@checkins.rss')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        xml_directive = '<?xml '
        self.assert_(body.startswith(xml_directive),
                     'checkins.rss has no XML directive:\n%s...' % body[:70])
        # Make sure the XML directive is not repeated
        self.assert_(body[len(xml_directive):].find(xml_directive) == -1,
                     '%s appears more than once in checkins.rss' % xml_directive)

    def test_add_simple_message(self):
        response = self.publish('/z3c/+/CheckinMessage',
                                basic='mgr:mgrpw',
                                form={'field.data': self.open('msg2.txt'),
                                      'UPDATE_SUBMIT': u'Submit'})
        self.assertEqual(response.getStatus(), 302)

        for view in self.container_views:
            response = self.publish('/z3c/@@%s' % view)
            self.assertEqual(response.getStatus(), 200)
        for view in self.message_views:
            response = self.publish('/z3c/msg2@example.org/@@%s' % view)
            self.assertEqual(response.getStatus(), 200)

        response = self.publish('/z3c/@@checkins.rss')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        xml_directive = '<?xml '
        self.assert_(body.startswith(xml_directive),
                     'checkins.rss has no XML directive:\n%s...' % body[:70])
        # Make sure the XML directive is not repeated
        self.assert_(body[len(xml_directive):].find(xml_directive) == -1,
                     '%s appears more than once in checkins.rss' % xml_directive)



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCheckins))
    return suite


if __name__ == '__main__':
    unittest.main()
