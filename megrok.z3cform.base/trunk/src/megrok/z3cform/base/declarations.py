# -*- coding: utf-8 -*-

import sys

from zope.interface import implementer
from z3c.form.validator import InvariantsValidator
from z3c.form.widget import ComputedWidgetAttribute
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from z3c.form.interfaces import IValidator, IManagerValidator
from z3c.form.validator import WidgetsValidatorDiscriminators


class DecoratedInvariantsValidator(InvariantsValidator):
    """ Decorator for Invariants"""

    def __init__(self, fn, context, request, view, schema, manager):
        super(DecoratedInvariantsValidator, self).__init__(
                              context, request, view, schema, manager)
        self.fn = fn

    def validateObject(self, obj):
        errors = super(DecoratedInvariantsValidator, self).validateObject(obj)
        error = self.fn(obj)
        if error:
            errors += error
        return errors


class invariant(object):
    """Decorator for functions to be registered as validator for invairants
    """

    def __init__(self, **kw):
        self.discriminators = kw

    def __call__(self, fn):

        @implementer(IManagerValidator)
        def factory(context, request, view, schema, manager):
            return DecoratedInvariantsValidator(
                        fn, context, request, view, schema, manager)

        WidgetsValidatorDiscriminators(factory, **self.discriminators)

        frame = sys._getframe(1)
        adapters = frame.f_locals.get('__form_validator_adapters__', None)
        if adapters is None:
            frame.f_locals['__form_validator_adapters__'] = adapters = []
        adapters.append(factory)

        return fn


class DecoratedValidator(SimpleFieldValidator):

    def __init__(self, fn, context, request, view, field, widget):
        super(DecoratedValidator, self).__init__(
                           context, request, view, field, widget)
        self.fn = fn

    def validate(self, value):
        super(DecoratedValidator, self).validate(value)
        self.fn(value)


class validator(object):
    """Decorator for functions to be registered as validators
    """

    def __init__(self, **kw):
        self.discriminators = kw

    def __call__(self, fn):

        @implementer(IValidator)
        def factory(context, request, view, field, widget):
            return DecoratedValidator(
                fn, context, request, view, field, widget)

        WidgetValidatorDiscriminators(factory, **self.discriminators)

        frame = sys._getframe(1)
        adapters = frame.f_locals.get('__form_validator_adapters__', None)
        if adapters is None:
            frame.f_locals['__form_validator_adapters__'] = adapters = []
        adapters.append(factory)

        return fn


class _computed_value(object):
    """Decorator for things using z3c.form.value IValue creators.
    """

    # should be set by subclass
    factory = None

    def __init__(self, name, **kw):
        self.name = name
        self.discriminators = kw

    def __call__(self, ob):

        try:
            value_adapter = (self.factory(ob, **self.discriminators), self.name)
        except ValueError, e:
            raise ValueError(u"Error constructing value adapter for %s: %s" % (str(ob), str(e)))

        frame = sys._getframe(1)
        adapters = frame.f_locals.get('__form_value_adapters__', None)
        if adapters is None:
            frame.f_locals['__form_value_adapters__'] = adapters = []
        adapters.append(value_adapter)
return ob


class default_value(_computed_value):
    """Decorator for functions providing a default field value when rendering the form
    """

    factory = ComputedWidgetAttribute

    def __init__(self, context=None, request=None, view=None, field=None, widget=None, form=None, layer=None):
        if not field and not widget:
            raise TypeError(u"Either 'field' or 'widget' must be specified")

        if form and view:
            raise TypeError(u"You cannot specify both 'view' and 'form' - one is an alias for the other")
        elif form and not view:
            view = form

        if request and layer:
            raise TypeError(u"You cannot specify both 'request' and 'layer' - one is an alias for the other")
        elif layer and not request:
            request = layer

        super(default_value, self).__init__('default',
                context=context,
                request=request,
                view=view,
                field=field,
                widget=widget,
            )
