from zope import interface, component

from zope.proxy import ProxyBase, getProxiedObject
from zope.security.checker import NamesChecker,defineChecker
from zope.security.proxy import removeSecurityProxy
from zope.decorator import DecoratorSpecificationDescriptor
from zope.decorator import DecoratedSecurityCheckerDescriptor
from zope.location import location
from zope.location.interfaces import ILocation
from zope.formlib.interfaces import IForm

from z3c.multiform.interfaces import ISelection, IFormLocation


class FormLocationSelection(object):

    __doc__ = """

    FormLocation to Selection adapter

    >>> from zope.publisher.browser import TestRequest
    >>> from zope import interface
    >>> class L(object):
    ...     __name__ = u'name'
    >>> l= L()
    >>> class F(object):
    ...     request = TestRequest()
    ...     context = 1
    ...     prefix = u"form.n1"
    >>> f = F()
    >>> p = FormLocationProxy(l, f)
    >>> p = FormLocationSelection(p)
    >>> p.selected
    False
    >>> p.selected = True
    >>> p.selected
    True
    >>> p.selected = False
    >>> p.selected
    False
    """

    interface.implements(ISelection)
    component.adapts(IFormLocation)

    def __init__(self,context):
        self.context = context

    def _setSelected(self,v):
        key = '_mf_selection.' + removeSecurityProxy(
            self.context.__form__).prefix
        form = removeSecurityProxy(self.context.__form__)
        form.request.form[key] = v

    def _getSelected(self):
        key = '_mf_selection.' + removeSecurityProxy(
            self.context.__form__).prefix
        res =  removeSecurityProxy(
            self.context.__form__).request.form.get(key,False)
        return res

    selected = property(_getSelected ,_setSelected)
        

class FormLocationProxy(ProxyBase):

    __doc__ = """Form Location-object proxy

    XXX the attributes of the form are not available because of a
    security proxy issue

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
    PicklingError: Can't pickle <class 'z3c.multiform.selection.L'...

    Proxies should get their doc strings from the object they proxy:

    >>> p.__doc__ == l.__doc__
    True

    """

#    interface.implements(IFormLocation)
    interface.implementsOnly(IFormLocation)
    component.adapts(ILocation, IForm)

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

formLocationChecker = NamesChecker(['__form__'])
defineChecker(FormLocationProxy, formLocationChecker)

