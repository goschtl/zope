"""Five specific directives.
"""
import os
from zope.interface import classImplements, Interface
from zope.component import getService, getGlobalService,\
     ComponentLookupError
from zope.configuration.exceptions import ConfigurationError
from zope.component.servicenames import Adapters, Presentation
from zope.publisher.interfaces.browser import IBrowserRequest
from provideinterface import provideInterface
from viewattribute import ViewAttribute
from viewable import Viewable

#def handler(serviceName, methodName, *args, **kwargs):
#    method=getattr(getService(serviceName), methodName)
#    method(*args, **kwargs)

def handler(serviceName, methodName, *args, **kwargs):
    method=getattr(getGlobalService(serviceName), methodName)
    method(*args, **kwargs)

def page(_context, name, for_,
         layer='default', template=None, class_=None,
         attribute='__call__', menu=None, title=None, 
         ):

    try:
        s = getGlobalService(Presentation)
    except ComponentLookupError, err:
        pass

    if not (class_ or template):
        raise ConfigurationError("Must specify a class or template")

    if attribute != '__call__':
        if template:
            raise ConfigurationError(
                "Attribute and template cannot be used together.")

        if not class_:
            raise ConfigurationError(
                "A class must be provided if attribute is used")

    if template:
        template = os.path.abspath(str(_context.path(template)))
        if not os.path.isfile(template):
            raise ConfigurationError("No such file", template)

    if class_:
        if attribute != '__call__':
            if not hasattr(class_, attribute):
                raise ConfigurationError(
                    "The provided class doesn't have the specified attribute "
                    )
        if template:
            # class and template
            new_class = SimpleViewClass(
                template, bases=(class_, ))
        else:
            #if not hasattr(class_, 'browserDefault'):
            #    cdict = {
            #        'browserDefault':
            #        lambda self, request: (getattr(self, attribute), ())
            #        }
            #else:
            #    cdict = {}
                
            #cdict['__page_attribute__'] = attribute
            class_.__page_attribute__ = attribute
            new_class = class_

    else:
        # template
        new_class = SimpleViewClass(template)

    _handle_for(_context, for_)

    _context.action(
        discriminator = ('view', for_, name, IBrowserRequest, layer),
        callable = handler,
        args = (Presentation, 'provideAdapter',
                IBrowserRequest, new_class, name, [for_], Interface, layer,
                _context.info),
        )

def _handle_for(_context, for_):
    if for_ is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', for_)
            )        

def implements(_context, class_, interface):
    for interface in interface:
        _context.action(
            discriminator = None,
            callable = classImplements,
            args = (class_, interface)
            )
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = (interface.__module__ + '.' + interface.getName(),
                    interface)
            )

def classViewable(class_):
    if hasattr(class_, '__bobo_traverse__'):
        raise TypeError("__bobo_traverse already__ exists on %s" % class_)
    setattr(class_, '__bobo_traverse__', Viewable.__bobo_traverse__)

def viewable(_context, class_):
    _context.action(
        discriminator = (class_,),
        callable = classViewable,
        args = (class_,)
        )
        
def layer(_context, name):

    _context.action(
        discriminator = ('layer', name),
        callable = handler,
        args = (Presentation, 'defineLayer', name, _context.info)
        )

def skin(_context, name, layers):
    if ',' in layers:
        raise TypeError("Commas are not allowed in layer names.")

    _context.action(
        discriminator = ('skin', name),
        callable = handler,
        args = (Presentation, 'defineSkin', name, layers, _context.info)
        )

def defaultSkin(_context, name):
    _context.action(
        discriminator = 'defaultSkin',
        callable = handler,
        args = (Presentation, 'setDefaultSkin', name, _context.info)
        )
