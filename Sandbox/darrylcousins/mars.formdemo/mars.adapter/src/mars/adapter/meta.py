import zope.interface
import zope.component

import grok

import martian
from martian import util

import mars.adapter

class AdapterFactoryGrokker(martian.ClassGrokker):
    component_class = mars.adapter.AdapterFactory

    def grok(self, name, factory, context, module_info, templates):
        adapter_context = util.determine_class_context(factory, context)
        provides = util.class_annotation(factory, 'grok.provides', None)
        name = util.class_annotation(factory, 'grok.name', '')
        factory = util.class_annotation(factory, 'mars.adapter.factory', None)
        #print '\nName: ', name, 'Factory:', factory, '\n'
        if factory is None:
            # TODO error message
            pass
        else:
            #zope.component.provideAdapter(factory, adapts=(zope.interface.Interface,),
            #                         provides=provides,
            #                         name=name)
            zope.component.provideAdapter(factory,
                                     name=name)
        return True

