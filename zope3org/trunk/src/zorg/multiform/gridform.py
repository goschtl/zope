from interfaces import ISelection,IFormLocation,IGridForm,IGridItemForm
from zope.schema.fieldproperty import FieldProperty
from zope.interface import implements
from zope.proxy import ProxyBase, getProxiedObject
from zope.app.decorator import DecoratorSpecificationDescriptor
from zope.app.decorator import DecoratedSecurityCheckerDescriptor
from zope.app.location import location
import multiform
from zope.formlib import namedtemplate
from zope.app.pagetemplate import ViewPageTemplateFile


default_grid_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('grid.pt'), IGridForm)

default_griditem_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('griditem.pt'), IGridItemForm)


class FormLocationSelection(object):

    implements(ISelection)

    def __init__(self,context):
        self.key = '_mf_selection.' + context.__form__.prefix + \
                   "." + context.__name__
        self.request = context.__form__.request

    def _setSelected(self,v):
        self.request.form[self.key]=v

    def _getSelected(self):
        self.request.form.get(self.key,False)

    selected = property(_getSelected,_setSelected)
        

class FormLocationProxy(ProxyBase):

    __doc__ = """Form Location-object proxy

    This is a non-picklable proxy that can be put around objects that
    implement `ILocation`.

    >>> from zope import interface
    >>> class IMarker(interface.Interface): pass
    >>> class L(object):
    ...     x = 1
    >>> l = L()
    >>> interface.directlyProvides(l,IMarker)
    >>> p = FormLocationProxy(l, "Form")
    >>> p.x
    1
    >>> p.x=2
    >>> p.x
    2
    >>> l.x
    2
    >>> p.__form__
    'Form'

    >>> IFormLocation.providedBy(p)
    True

    >>> IMarker.providedBy(p)
    True

    >>> import pickle
    >>> p2 = pickle.dumps(p)
    Traceback (most recent call last):
    ...
    TypeError: Not picklable

    Proxies should get their doc strings from the object they proxy:

    >>> p.__doc__ == l.__doc__
    True

    """

    implements(IFormLocation)

    __slots__ = '__form__'
    __safe_for_unpickling__ = True

    def __new__(self, ob, form):
        return ProxyBase.__new__(self, ob)

    def __init__(self, ob, form):
        ProxyBase.__init__(self, ob)
        self.__form__ = form

    def __reduce__(self, proto=None):
        raise TypeError("Not picklable")


    __doc__ = location.ClassAndInstanceDescr(
        lambda inst: getProxiedObject(inst).__doc__,
        lambda cls, __doc__ = __doc__: __doc__,
        )
    
    __reduce_ex__ = __reduce__

    __providedBy__ = DecoratorSpecificationDescriptor()

    __Security_checker__ = DecoratedSecurityCheckerDescriptor()



class GridItemFormBase(multiform.ItemFormBase):
    implements(IGridItemForm)
    template = namedtemplate.NamedTemplate('default')

class GridFormBase(multiform.MultiFormBase):
    implements(IGridForm)
    template = namedtemplate.NamedTemplate('default')
