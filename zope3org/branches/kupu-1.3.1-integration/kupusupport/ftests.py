import unittest
from zope.app.tests import ztapi
from zope.app.tests.functional import BrowserTestCase

class Test(BrowserTestCase):

    def setUp(self):
        BrowserTestCase.setUp(self)

    def test_common_kupubasetools_js(self):
        response = self.publish('/++resource++common/kupubasetools.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupucontentfilters_js(self):
        response = self.publish('/++resource++common/kupucontentfilters.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupucontextmenu_js(self):
        response = self.publish('/++resource++common/kupucontextmenu.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupudrawers_js(self):
        response = self.publish('/++resource++common/kupudrawers.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupudrawerstyles_css(self):
        response = self.publish('/++resource++common/kupudrawerstyles.css')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupueditor_js(self):
        response = self.publish('/++resource++common/kupueditor.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupuhelpers_js(self):
        response = self.publish('/++resource++common/kupuhelpers.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupuinit_js(self):
        response = self.publish('/++resource++common/kupuinit.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupuloggers_js(self):
        response = self.publish('/++resource++common/kupuloggers.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupusaveonpart_js(self):
        response = self.publish('/++resource++common/kupusaveonpart.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupusourceedit_js(self):
        response = self.publish('/++resource++common/kupusourceedit.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_kupustart_js(self):
        response = self.publish('/++resource++common/kupustart.js')
        self.assertEqual(response.getStatus(), 200)

    def test_common_sarissa_js(self):
        response = self.publish('/++resource++common/sarissa.js')
        self.assertEqual(response.getStatus(), 200)

    def test_drawer_xsl(self):
        response = self.publish('/++resource++drawer.xsl')
        self.assertEqual(response.getStatus(), 200)
      
    def test_imagelibrary1_xml(self):
        response = self.publish('/++resource++imagelibrary1.xml')
        self.assertEqual(response.getStatus(), 200)

    def test_kupudrawers_linklibrary_xml(self):
        response = self.publish('/++resource++kupudrawers/linklibrary.xml')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_background_color_png(self):
        response = self.publish('/++resource++kupuimages/background-color.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_bold_png(self):
        response = self.publish('/++resource++kupuimages/bold.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_definitionlist_png(self):
        response = self.publish('/++resource++kupuimages/definitionlist.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_exit_gif(self):
        response = self.publish('/++resource++kupuimages/exit.gif')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_hr_png(self):
        response = self.publish('/++resource++kupuimages/hr.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_kupu_icon_gif(self):
        response = self.publish('/++resource++kupuimages/kupu_icon.gif')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_indent_png(self):
        response = self.publish('/++resource++kupuimages/indent.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_italic_png(self):
        response = self.publish('/++resource++kupuimages/italic.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_justify_center_png(self):
        response = self.publish('/++resource++kupuimages/')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_justify_left_png(self):
        response = self.publish('/++resource++kupuimages/justify-left.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_justify_right_png(self):
        response = self.publish('/++resource++kupuimages/justify-right.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_kupulibrary_png(self):
        response = self.publish('/++resource++kupuimages/kupulibrary.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_link_png(self):
        response = self.publish('/++resource++kupuimages/link.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_ordered_list_png(self):
        response = self.publish('/++resource++kupuimages/ordered-list.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_outdent_png(self):
        response = self.publish('/++resource++kupuimages/outdent.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_redo_png(self):
        response = self.publish('/++resource++kupuimages/redo.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_remove_png(self):
        response = self.publish('/++resource++kupuimages/remove.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_save_png(self):
        response = self.publish('/++resource++kupuimages/save.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_space_gif(self):
        response = self.publish('/++resource++kupuimages/space.gif')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_subscript_png(self):
        response = self.publish('/++resource++kupuimages/subscript.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_superscript_png(self):
        response = self.publish('/++resource++kupuimages/superscript.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_table_png(self):
        response = self.publish('/++resource++kupuimages/table.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_underline_png(self):
        response = self.publish('/++resource++kupuimages/underline.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_undo_png(self):
        response = self.publish('/++resource++kupuimages/undo.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_unordered_list_png(self):
        response = self.publish('/++resource++kupuimages/unordered-list.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupuimages_view_source_png(self):
        response = self.publish('/++resource++kupuimages/view-source.png')
        self.assertEqual(response.getStatus(), 200)

    def test_kupustyles_css(self):
        response = self.publish('/++resource++kupustyles.css')
        self.assertEqual(response.getStatus(), 200)

def test_suite():
    return unittest.makeSuite(Test)
