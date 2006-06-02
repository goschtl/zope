import doctest
import unittest
import location

from zope import component
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
import zope.schema.interfaces
import zope.app.form.browser
import zope.publisher.interfaces.browser
import zope.app.form.interfaces
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.annotation.interfaces import IAnnotatable
from zope.app.location.interfaces import ILocation
from zope.formlib import form

from z3c.multiform import gridform,multiform,selection
from z3c.multiform.interfaces import IFormLocation,ISelection
from interfaces import IMovableLocation


def setUp(test):
    setup.placefulSetUp()

    component.provideAdapter(
        zope.app.form.browser.DatetimeDisplayWidget,
        [zope.schema.interfaces.IDatetime,
         zope.publisher.interfaces.browser.IBrowserRequest,
         ],
        zope.app.form.interfaces.IDisplayWidget,
        )

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
        IFormLocation
        )
    component.provideAdapter(
        selection.FormLocationSelection,
        [IFormLocation],
        ISelection
        )
    component.provideAdapter(
        location.MovableLocation,
        [ILocation],
        IMovableLocation
        )
    component.provideAdapter(
        ZDCAnnotatableAdapter,
        [IAnnotatable],
        IWriteZopeDublinCore
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
        DocFileSuite('container.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
