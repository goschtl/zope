import os

import zope.interface
import zope.component
from zope.security.checker import NamesChecker, CheckerPublic
from zope.publisher.interfaces.browser import (IBrowserRequest,
                                                IDefaultBrowserLayer)
from zope.app.publisher.browser.fileresource import (FileResourceFactory,
                                                    ImageResourceFactory)
from zope.app.publisher.browser.directoryresource import DirectoryResourceFactory

import grok
from grok.util import (get_default_permission,
                        make_checker,
                        determine_class_directive)

import martian
from martian import util

import mars.resource

allowed_names = ('GET', 'HEAD', 'publishTraverse', 'browserDefault',
                 'request', '__call__')

class ResourceGrokker(martian.ClassGrokker):
    component_class = mars.resource.ResourceFactory

    def grok(self, name, factory, module_info, config, *kws):
        factory.module_info = module_info
        factory_name = factory.__name__.lower()

        # we need a path to the file containing the resource
        file_name = util.class_annotation(factory, 'mars.resource.file', '')
        image_name = util.class_annotation(factory, 'mars.resource.image', '')
        if file_name == '' and image_name == '':
            raise GrokError("Either mars.resource.file or mars.resource.image"
                            " must be defined for %s."
                            % (factory.__name__),
                            factory)

        file = image = None
        if image_name != '':
            file_name = image_name
            image = filepath = os.path.join(os.path.dirname(module_info.path), file_name)
        else:
            file = filepath = os.path.join(os.path.dirname(module_info.path), file_name)

        if not os.path.exists(filepath):
            filepath = None
            # allow for absolute path to resource
            if os.path.exists(file_name):
                filepath = file_name
        if filepath is None:
            raise GrokError("No resource found for %s using path %s."
                            " Please use mars.resource.file or"
                            " mars.resource.image to define path to the"
                            " file containing the resource"
                            % (factory.__name__, file_name),
                            factory)

        view_layer = determine_class_directive('grok.layer',
                                               factory, module_info,
                                               default=IDefaultBrowserLayer)
        view_name = util.class_annotation(factory, 'grok.name', '')

        checker = NamesChecker(allowed_names)
        if file:
            factory = FileResourceFactory(file, checker, view_name)
        elif image:
            factory = ImageResourceFactory(image, checker, view_name)

        adapts = (view_layer, )

        config.action(
            discriminator=('adapter', adapts,
                            IBrowserRequest, view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, 
                            IBrowserRequest, view_name),
            )

        return True

class ResourceDirectoryGrokker(martian.ClassGrokker):
    component_class = mars.resource.ResourceDirectoryFactory

    def grok(self, name, factory, module_info, config, *kws):
        factory.module_info = module_info
        factory_name = factory.__name__.lower()

        # we need a path to the file containing the resource
        directory_name = util.class_annotation(factory, 'mars.resource.directory', '')
        directory = os.path.join(os.path.dirname(module_info.path), directory_name)

        if not os.path.isdir(directory):
            raise GrokError("No directory found for %s using path %s."
                            " Please use mars.resource.directory"
                            " to define path to the directory."
                            % (factory.__name__, directory_name),
                            factory)

        view_layer = determine_class_directive('grok.layer',
                                               factory, module_info,
                                               default=IDefaultBrowserLayer)
        view_name = util.class_annotation(factory, 'grok.name', factory_name)

        checker = NamesChecker(allowed_names)
        factory = DirectoryResourceFactory(directory, checker, view_name)

        adapts = (view_layer, )

        config.action( 
            discriminator=('adapter', adapts, IBrowserRequest, view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, IBrowserRequest, view_name),
            )
        return True


