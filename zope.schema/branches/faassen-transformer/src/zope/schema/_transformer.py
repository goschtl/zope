from zope.interface.interface import InterfaceClass
from zope.schema import getFieldNamesInOrder

class transformer(object):
    def __init__(self, schema):
        self.schema = schema

    def select(self, names):
        attrs = {}
        order = 0
        for name in names:
            attrs[name] = self._copy_field(self.schema[name],
                                           order=order)
            order += 1
            
        return self._transformer(attrs)

    def omit(self, names):
        attrs = {}
        order = 0
        for name in getFieldNamesInOrder(self.schema):
            if name not in names:
                attrs[name] = self._copy_field(self.schema[name],
                                               order=order)
            order += 1

        return self._transformer(attrs)

    def override(self, name, **kw):
        attrs = {}
        order = 0
        for name in getFieldNamesInOrder(self.schema):
            attrs[name] = self._copy_field(self.schema[name],
                                           order=order,
                                           **kw)
            order += 1
        return self._transformer(attrs)
    
    def add(self, field, name=None, before=None):
        attrs = {}
        order = 0
        added = False
        add_name = name
        for name in getFieldNamesInOrder(self.schema):
            if not added and name == before:
                field.order = order
                if add_name is not None:
                    field.__name__ = add_name
                attrs[field.__name__] = field
                order += 1
                added = True
            attrs[name] = self._copy_field(self.schema[name],
                                           order=order)
            order += 1
        if not added:
            if add_name is not None:
                field.__name__ = add_name
            field.order = order
            attrs[field.__name__] = field
            
        return self._transformer(attrs)
    
    def _transformer(self, attrs):
        return transformer(InterfaceClass(name=self.schema.__name__,
                                          bases=self.schema.__bases__,
                                          __module__=self.schema.__module__,
                                          attrs=attrs))
    
    def _copy_field(self, field, **kw):
        # by passing None as context, we can trick the binding
        # machinery into making a straight copy
        clone = field.bind(None)
        for key, value in kw.items():
            setattr(clone, key, value)
        return clone

