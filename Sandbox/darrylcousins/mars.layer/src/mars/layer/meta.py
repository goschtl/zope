import martian
import grok
import zope.component
from zope.publisher.interfaces.browser import (IBrowserRequest,
                                               IBrowserSkinType)
from martian import util
import mars.layer
from mars.layer.components import ILayer

class ILayerGrokker(martian.ClassGrokker):
    component_class = ILayer

class SkinGrokker(martian.ClassGrokker):
    component_class = mars.layer.Skin

    def grok(self, name, factory, context, module_info, templates):
        layer = util.class_annotation(factory, 'mars.layer.layer',
                                    None) or module_info.getAnnotation('mars.layer.layer',
                                    None) or IBrowserRequest
        name = grok.util.class_annotation(factory, 'grok.name', factory.__name__.lower())
        #print '\nName: ', name, 'Factory: ', factory, 'layer: ', layer, '\n'
        zope.component.interface.provideInterface(name, layer, IBrowserSkinType)

        return True
