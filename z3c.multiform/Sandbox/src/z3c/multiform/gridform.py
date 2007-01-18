
from zope import component, interface
from zope.formlib import namedtemplate
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.location.interfaces import ILocation

from interfaces import IGridForm, IGridItemForm, ISorter
import multiform


default_grid_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('grid.pt'), IGridForm)

default_griditem_template = namedtemplate.NamedTemplateImplementation(
    ViewPageTemplateFile('griditem.pt'), IGridItemForm)


class GridItemFormBase(multiform.ItemFormBase):

    interface.implements(IGridItemForm)

    template = namedtemplate.NamedTemplate('default')


class GridFormBase(multiform.MultiFormBase):

    interface.implements(IGridForm)

    default_batch_size = None
    default_sort_on = None
    default_sort_reverse = None

    template = namedtemplate.NamedTemplate('default')

    def __init__(self, context, request):
        context = FilterMapping(context, request, self)
        super(GridFormBase,self).__init__(context, request)
        

class FilterMapping(object):
    
    interface.implements(ILocation)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        if ILocation.providedBy(context):
            self.__parent__ = context.__parent__
            self.__name__ = context.__name__
            
        else:
            self.__parent__ = None
            self.__name__ = u""
        self.form = form

        self.batch_start = request.form.get(
                           '%s.handle.batch_start' % form.prefix,0)
        self.batch_size = request.form.get(
                           '%s.handle.batch_size' % form.prefix,
                           form.default_batch_size)
        self.sort_on = request.form.get(
                           '%s.handle.sort_on' % form.prefix,
                           form.default_sort_on)
        self.sort_reverse = request.form.get(
                           '%s.handle.sort_reverse' % form.prefix,
                           form.default_sort_reverse)

    def sortAllKeys(self):
        sorter = None
        if self.sort_on:
            sortName = self.sort_on
            sortField = None
            for field in self.form.itemFormFactory.form_fields:
                if field.__name__ == sortName:
                    sortField = field
                    break
            if sortField:
                sorter = component.getMultiAdapter((sortField.field.interface,
                                                    sortField.field),
                                                   ISorter)
        if sorter:
            items = sorter.sort(self.context.items())
            if self.sort_reverse:
                items.reverse()
            keys = []
            for key, value in items:
                yield key
        else:
            for key in self.context.keys():
                yield key

    def keys(self):
        sortKeys = self.sortAllKeys()
        batch_start = self.batch_start or 0
        batch_size = self.batch_size or 0
        if not self.batch_size:
            if not batch_start:
                for k in sortKeys:
                    yield k
                raise StopIteration
            batch_end = None
        else:
            batch_end = batch_start + batch_size
        for i, key in enumerate(sortKeys):
            if batch_end is not None and i >= batch_end:
                return
            if i >= batch_start:
                yield key

    def values(self):
        for k in self.keys():
            yield self.context[k]

    def items(self):
        for k in self.keys():
            yield k, self.context[k]

    def __iter__(self):
        return iter(self.keys())

    def __getitem__(self, key):
        '''See interface `IReadContainer`'''
        if key in self.keys():
            return self.context[key]
        else:
            raise KeyError, key

    def get(self, key, default=None):
        '''See interface `IReadContainer`'''
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __len__(self):
        '''See interface `IReadContainer`'''
        return len(tuple(self.keys()))

    def __contains__(self, key):
        '''See interface `IReadContainer`'''
        return key in self.keys()

    has_key = __contains__

    def __setitem__(self, key, object):
        '''See interface `IWriteContainer`'''
        self.context.__setitem__(key, object)

    def __delitem__(self, key):
        '''See interface `IWriteContainer`'''
        if key in self.keys():
            self.context.__delitem__(key)
        else:
            raise KeyError, key
