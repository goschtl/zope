import traject
import martian
from megrok.traject import components, directive
import grokcore.component
from zope import component
from zope.publisher.interfaces.browser import (IBrowserPublisher)
from zope.publisher.interfaces.http import IHTTPRequest

class TrajectGrokker(martian.ClassGrokker):
    martian.component(components.Traject)

    martian.directive(grokcore.component.context)

    def execute(self, factory, config, context, **kw):
        pattern_str = factory.pattern
        model = factory.model
        factory_func = factory.factory.im_func
        arguments_func = factory.arguments.im_func

        _register_traject(config, context, pattern_str, model,
                          factory_func, arguments_func)
        return True
    
class ModelGrokker(martian.ClassGrokker):
    martian.component(components.Model)

    martian.directive(grokcore.component.context)
    martian.directive(directive.pattern)
    
    def execute(self, factory, config, context, pattern, **kw):
        pattern_str = pattern
        model = factory
        factory_func = factory.factory.im_func
        arguments_func = factory.arguments.im_func

        _register_traject(config, context, pattern_str, model,
                          factory_func, arguments_func)
        return True

def _register_traject(config, context,
                      pattern_str, model, factory_func, arguments_func):
    # register
    config.action(
        discriminator=('traject.register', context, pattern_str),
        callable=traject.register,
        args=(context, pattern_str, factory_func),
        )

    # register_inverse
    config.action(
        discriminator=('traject.register_inverse', context, model,
                       pattern_str),
        callable=traject.register_inverse,
        args=(context, model, pattern_str, arguments_func))
    
    # register traverser on context; overwrite previous as they're
    # all the same
    config.action(
        discriminator=object(), # we always want a different discriminator
        callable=component.provideAdapter,
        args=(components.TrajectTraverser, (context, IHTTPRequest),
              IBrowserPublisher),
        )
