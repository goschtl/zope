import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope import component
import zope.schema.interfaces
import zope.app.form.browser
import zope.publisher.interfaces.browser
import zope.app.form.interfaces
import interfaces
import gridform
import multiform
import selection
import sort
from zope.formlib import form

def setUp(test):
    setup.placefulSetUp()

    component.provideAdapter(
        zope.app.form.browser.TextWidget,
        [zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IInputWidget,
        )
    component.provideAdapter(
        zope.app.form.browser.UnicodeDisplayWidget,
        [zope.schema.interfaces.ITextLine,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )
    component.provideAdapter(
        zope.app.form.browser.boolwidgets.BooleanDisplayWidget,
        [zope.schema.interfaces.IBool,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )
    component.provideAdapter(
        zope.app.form.browser.CheckBoxWidget,
        [zope.schema.interfaces.IBool,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IInputWidget,
        )
    component.provideAdapter(
        zope.app.form.browser.UnicodeDisplayWidget,
        [zope.schema.interfaces.IInt,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )
    component.provideAdapter(
        zope.app.form.browser.IntWidget,
        [zope.schema.interfaces.IInt,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IInputWidget,
        )
    component.provideAdapter(
        selection.FormLocationProxy,
        [zope.app.location.interfaces.ILocation,
         zope.formlib.interfaces.IForm
         ],
        interfaces.IFormLocation
        )
    component.provideAdapter(
        selection.FormLocationSelection,
        [interfaces.IFormLocation],
        interfaces.ISelection
        )
    component.provideAdapter(
        sort.SchemaSorter,
        [zope.interface.Interface,
         zope.schema.interfaces.IField],
        interfaces.ISorter
        )    
    component.provideAdapter(gridform.default_grid_template,
                             name="default")
    component.provideAdapter(gridform.default_griditem_template,
                             name="default")
    component.provideAdapter(form.render_submit_button, name='render')
    component.provideAdapter(multiform.render_submit_button, name='render')
    
def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    
    return unittest.TestSuite(
        (
        DocTestSuite('multiform.selection',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('actions.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('gridform.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
