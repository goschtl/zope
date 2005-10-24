##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser directives

Directives to emulate the 'http://namespaces.zope.org/browser'
namespace in ZCML known from zope.app.

$Id$
"""
import os
from Globals import InitializeClass as initializeClass

from zope.component import ComponentLookupError
from zope.configuration.exceptions import ConfigurationError
from zope.publisher.interfaces.browser import IBrowserRequest,\
     IDefaultBrowserLayer

from zope.app.component.metaconfigure import handler
from zope.app.publisher.browser.viewmeta import pages as zope_app_pages
from zope.app.publisher.browser.viewmeta import view as zope_app_view
from zope.app.publisher.browser.viewmeta import page as zope_app_page

from Products.Five.security import getSecurityInfo, protectClass, protectName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser.resource import FileResourceFactory,\
     ImageResourceFactory, PageTemplateResourceFactory, DirectoryResourceFactory

def getLastClass(_context):
    """Retrieve the last action from the ZCML _context and return its
    class so that we can do some munging with it."""
    last_action = _context.actions[-1]
    args = last_action[2]
    directive, (for_, layer), dummy, name, last_class, context_info = args
    return last_class

def page(_context, name, permission, for_,
         layer=IDefaultBrowserLayer, template=None, class_=None,
         allowed_interface=None, allowed_attributes=None,
         attribute='__call__', menu=None, title=None):
    zope_app_page(_context, name, permission, for_,
                  layer, template, class_, allowed_interface,
                  allowed_attributes, attribute, menu, title)
    last_class = getLastClass(_context)

    # replace the class's index with Five's page template version
    if template:
        last_class.index = ZopeTwoPageTemplateFile(last_class.index.filename)

    # make class traversing be Zope 2 compliant
    if class_ and not template:
        last_class.__browser_default__ = lambda self, request: \
                                         self, (self.__page_attribute__,)
        # this is technically not needed because ZPublisher finds our
        # attribute through __browser_default__; but we also want to
        # be able to call pages from python modules, PythonScripts or
        # ZPT
        last_class.__call__ = lambda *args, **kw: \
                              getattr(self, attribute)(*args, **kw)

    # in case the attribute does not provide a docstring,
    # ZPublisher refuses to publish it. So, as a workaround,
    # we provide a stub docstring
    func = getattr(last_class, attribute)
    if not func.__doc__:
        # cannot test for MethodType/UnboundMethod here
        # because of ExtensionClass
        # XXX should be able to do this now, but don't know what was
        # meant
        if hasattr(func, 'im_func'):
            # you can only set a docstring on functions, not
            # on method objects
            func = func.im_func
        func.__doc__ = "Stub docstring to make ZPublisher work"

    # now squeeze explicit acquisition into the damn thing
    #if Acquisition.Explicit not in last_class.__mro__:
    #    last_class.__bases__ = (Acquisition.Explicit,) + last_class.__bases__
    
    # Zope 2 security
    if allowed_attributes is None:
        allowed_attributes = []
    if allowed_interface is not None:
        for interface in allowed_interface:
            allowed_attributes.extend(interface.names())
    _context.action(
        discriminator = ('five:protectClass', last_class),
        callable = protectClass,
        args = (last_class, permission)
        )
    if allowed_attributes:
        for attr in allowed_attributes:
            _context.action(
                discriminator = ('five:protectName', last_class, attr),
                callable = protectName,
                args = (last_class, attr, permission)
                )
    _context.action(
        discriminator = ('five:initialize:class', last_class),
        callable = initializeClass,
        args = (last_class,)
        )

class pages(zope_app_pages):

    def page(self, _context, name, attribute='__call__', template=None,
             menu=None, title=None):
        return page(_context,
                    name=name,
                    attribute=attribute,
                    template=template,
                    menu=menu, title=title,
                    **(self.opts))

# view (named view with pages)

class view(zope_app_view):

    def __call__(self):
        super(view, self).__call__()
        _context = self.args[0]
        last_class = getLastClass(_context)
        # override Z3 templates with Five templates
        for pname, attribute, template in self.pages:
            if template:
                last_class.pname = ZopeTwoPageTemplateFile(template)
        # XXX probably need to do more patching to make it a ZPublisher
        # compliant view class

## _factory_map = {'image':{'prefix':'ImageResource',
##                          'count':0,
##                          'factory':ImageResourceFactory},
##                 'file':{'prefix':'FileResource',
##                         'count':0,
##                         'factory':FileResourceFactory},
##                 'template':{'prefix':'PageTemplateResource',
##                             'count':0,
##                             'factory':PageTemplateResourceFactory}
##                 }

## def resource(_context, name, layer='default', permission='zope.Public',
##              file=None, image=None, template=None):

##     if ((file and image) or (file and template) or
##         (image and template) or not (file or image or template)):
##         raise ConfigurationError(
##             "Must use exactly one of file or image or template"
##             "attributes for resource directives"
##             )

##     res = file or image or template
##     res_type = ((file and 'file') or
##                  (image and 'image') or
##                  (template and 'template'))
##     factory_info = _factory_map.get(res_type)
##     factory_info['count'] += 1
##     res_factory = factory_info['factory']
##     class_name = '%s%s' % (factory_info['prefix'], factory_info['count'])
##     new_class = makeClass(class_name, (res_factory.resource,), {})
##     factory = res_factory(name, res, resource_factory=new_class)

##     _context.action(
##         discriminator = ('resource', name, IBrowserRequest, layer),
##         callable = handler,
##         args = (Presentation, 'provideResource',
##                 name, IBrowserRequest, factory, layer),
##         )
##     _context.action(
##         discriminator = ('five:protectClass', new_class),
##         callable = protectClass,
##         args = (new_class, permission)
##         )
##     _context.action(
##         discriminator = ('five:initialize:class', new_class),
##         callable = initializeClass,
##         args = (new_class,)
##         )

## _rd_map = {ImageResourceFactory:{'prefix':'DirContainedImageResource',
##                                  'count':0},
##            FileResourceFactory:{'prefix':'DirContainedFileResource',
##                                 'count':0},
##            PageTemplateResourceFactory:{'prefix':'DirContainedPTResource',
##                                         'count':0},
##            DirectoryResourceFactory:{'prefix':'DirectoryResource',
##                                      'count':0}
##            }

## def resourceDirectory(_context, name, directory, layer='default',
##                       permission='zope.Public'):

##     if not os.path.isdir(directory):
##         raise ConfigurationError(
##             "Directory %s does not exist" % directory
##             )

##     resource = DirectoryResourceFactory.resource
##     f_cache = {}
##     resource_factories = dict(resource.resource_factories)
##     resource_factories['default'] = resource.default_factory
##     for ext, factory in resource_factories.items():
##         if f_cache.get(factory) is not None:
##             continue
##         factory_info = _rd_map.get(factory)
##         factory_info['count'] += 1
##         class_name = '%s%s' % (factory_info['prefix'], factory_info['count'])
##         factory_name = '%s%s' % (factory.__name__, factory_info['count'])
##         f_resource = makeClass(class_name, (factory.resource,), {})
##         f_cache[factory] = makeClass(factory_name, (factory,),
##                                      {'resource':f_resource})
##     for ext, factory in resource_factories.items():
##         resource_factories[ext] = f_cache[factory]
##     default_factory = resource_factories['default']
##     del resource_factories['default']

##     cdict = {'resource_factories':resource_factories,
##              'default_factory':default_factory}

##     factory_info = _rd_map.get(DirectoryResourceFactory)
##     factory_info['count'] += 1
##     class_name = '%s%s' % (factory_info['prefix'], factory_info['count'])
##     dir_factory = makeClass(class_name, (resource,), cdict)
##     factory = DirectoryResourceFactory(name, directory,
##                                        resource_factory=dir_factory)

##     new_classes = [dir_factory,
##                    ] + [f.resource for f in f_cache.values()]

##     _context.action(
##         discriminator = ('resource', name, IBrowserRequest, layer),
##         callable = handler,
##         args = (Presentation, 'provideResource',
##                 name, IBrowserRequest, factory, layer),
##         )
##     for new_class in new_classes:
##         _context.action(
##             discriminator = ('five:protectClass', new_class),
##             callable = protectClass,
##             args = (new_class, permission)
##             )
##         _context.action(
##             discriminator = ('five:initialize:class', new_class),
##             callable = initializeClass,
##             args = (new_class,)
##             )

