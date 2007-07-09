__docformat__ = "reStructuredText"
import os
import unittest
from zope.app.testing import functional
from mars.formdemo import testing

def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()

def test_suite():
    suites = []
    for docpath in (
                    ('message', 'message.txt'),
                    ('questionnaire', 'questionnaire.txt'),
                    ('widgets', 'widgets.txt'),
                    ('spreadsheet', 'spreadsheet.txt'),
                    ('wizard', 'wizard.txt'),
                    ):
        suite = functional.FunctionalDocFileSuite(
            os.path.join(*docpath),
            setUp=testing.setUp,
            globs={'getRootFolder': getRootFolder})
        suite.layer = testing.FormDemoLayer
        suites.append(suite)
    return unittest.TestSuite(suites)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
