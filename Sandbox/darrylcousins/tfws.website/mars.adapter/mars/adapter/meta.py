import zope.interface
import zope.component

import grok

import martian
from martian.error import GrokError
from martian import util

import mars.adapter

class AdapterFactoryGrokker(martian.ClassGrokker):
    component_class = mars.adapter.AdapterFactory

    def grok(self, name, factory, module_info, config, *kws):
        name = util.class_annotation(factory, 'grok.name', '')
        adapter_factory = util.class_annotation(
                                    factory, 'mars.adapter.factory', None)
        provides = zope.component.registry._getAdapterProvided(adapter_factory)
        adapter_context = zope.component.registry._getAdapterRequired(
                                    adapter_factory, None)

        #print '\n',name,'\n',adapter_factory,'\n',provides,'\n',adapter_context

        if adapter_factory is None:
            raise GrokError(
                    "mars.adapter.factory must be provided for AdapterFactory"
                    )
        else:
            config.action( 
                discriminator=('adapter', adapter_context[0], provides, name),
                callable=zope.component.provideAdapter,
                args=(adapter_factory, adapter_context, provides, name),
                )

        return True
