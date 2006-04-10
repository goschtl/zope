from interfaces import IGridForm,IGridItemForm
from zope.interface import implements
import multiform
from zope.formlib import namedtemplate
from zope.app.pagetemplate import ViewPageTemplateFile


default_grid_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('grid.pt'), IGridForm)

default_griditem_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('griditem.pt'), IGridItemForm)


class GridItemFormBase(multiform.ItemFormBase):
    implements(IGridItemForm)
    template = namedtemplate.NamedTemplate('default')

class GridFormBase(multiform.MultiFormBase):
    implements(IGridForm)
    template = namedtemplate.NamedTemplate('default')
