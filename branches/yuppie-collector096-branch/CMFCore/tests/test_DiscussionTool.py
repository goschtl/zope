from unittest import TestCase, TestSuite, makeSuite, main

import Zope
try:
    from Interface.Verify import verifyClass
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import verify_class_implementation as verifyClass

from Products.CMFCore.DiscussionTool import DiscussionTool


class DiscussionToolTests(TestCase):

    def test_interface(self):
        from Products.CMFCore.interfaces.portal_discussion \
                import oldstyle_portal_discussion as IOldstyleDiscussionTool

        verifyClass(IOldstyleDiscussionTool, DiscussionTool)


def test_suite():
    return TestSuite((
        makeSuite( DiscussionToolTests ),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
