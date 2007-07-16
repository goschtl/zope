import zope.interface
import zope.component

import grok

import martian
from martian import util

import mars.adapter

class AdapterFactoryGrokker(martian.ClassGrokker):
    component_class = mars.adapter.AdapterFactory

    def grok(self, name, factory, context, module_info, templates):
        name = util.class_annotation(factory, 'grok.name', '')
        factory = util.class_annotation(factory, 'mars.adapter.factory', None)
        provided = zope.component.registry._getAdapterProvided(factory)
        required = zope.component.registry._getAdapterRequired(factory, None)
        #print '\nName: ', name, 'Factory:', factory, \
        #      'Provided: ', provided, 'Required: ', required, '\n'
        if factory is None:
            # error message
            pass
        else:
            zope.component.provideAdapter(factory, adapts=required, provides=provided,
                                     name=name)
        return True

