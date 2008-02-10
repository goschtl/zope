import zope.component
from zope.publisher.interfaces.browser import IBrowserView

from zope.viewlet.interfaces import IViewlet, IViewletManager

from martian import util

import mars.viewlet
from mars.view.meta import ViewGrokkerBase

class ViewletManagerGrokker(ViewGrokkerBase):
    component_class = mars.viewlet.ViewletManager
    provides = IViewletManager
    
    def register(self, factory, config):

        view = util.class_annotation(factory, 'mars.viewlet.view',
                                                   None) or IBrowserView
        zope.component.provideAdapter(factory,
                     adapts=(self.view_context, self.view_layer, view),
                     provides=self.provides,
                     name=self.view_name)
        adapts = (self.view_context, self.view_layer, view)

        config.action( 
            discriminator=('adapter', adapts, self.provides, self.view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, self.provides, self.view_name),
            )


class ViewletGrokker(ViewGrokkerBase):
    component_class = mars.viewlet.Viewlet
    provides = IViewlet

    def register(self, factory, config):

        manager = util.class_annotation(factory, 'mars.viewlet.manager',
                       None) or module_info.getAnnotation('mars.viewlet.manager',
                       None) or IViewletManager # IViewletManager?

        view = util.class_annotation(factory, 'mars.viewlet.view',
                       None) or IBrowserView

        adapts = (self.view_context, self.view_layer, view, manager)

        config.action( 
            discriminator=('adapter', adapts, self.provides, self.view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, self.provides, self.view_name),
            )

        #print '\nname:', self.view_name,'context:', self.view_context,'factory:', factory,\
        #      'layer:', self.view_layer, 'manager', manager, 'view: ', view,'\n'


class SimpleViewletGrokker(ViewGrokkerBase):
    component_class = mars.viewlet.SimpleViewlet
    provides = IViewlet

    def register(self, factory, config):

        manager = util.class_annotation(factory, 'mars.viewlet.manager',
                       None) or module_info.getAnnotation('mars.viewlet.manager',
                       None) or IViewletManager
        view = util.class_annotation(factory, 'mars.viewlet.view',
                       None) or IBrowserView

        adapts = (self.view_context, self.view_layer, view, manager)

        config.action( 
            discriminator=('adapter', adapts, self.provides, self.view_name),
            callable=zope.component.provideAdapter,
            args=(factory, adapts, self.provides, self.view_name),
            )

#        print '\nname:', self.view_name,'context:', self.view_context,'factory:', factory,\
#              'layer:', self.view_layer, 'manager', manager, 'view: ', view,'\n'

