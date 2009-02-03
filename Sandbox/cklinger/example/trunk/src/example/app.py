import grok
import megrok.pagelet
from zope.interface import Interface


### Skin
import z3c.formui.interfaces
from z3c.form.interfaces import IFormLayer
from z3c.layer.pagelet import IPageletBrowserLayer

class MySkinLayer(grok.IBrowserRequest, IFormLayer):
    pass

class MySkin(z3c.formui.interfaces.IDivFormLayer, MySkinLayer):
    grok.skin('myskin')


grok.layer(MySkin)

class Example(grok.Application, grok.Container):
    pass

class Index(grok.View):
    pass # see app_templates/index.pt


class ExampleLayout(megrok.pagelet.LayoutView):
    """ This is our general Layout Template"""
    grok.context(Interface)
    megrok.pagelet.template('layout.pt')

class Start(megrok.pagelet.Pagelet):
    """ This is a simple Pagelet which is renderd in the Layout Template"""
    grok.context(Example)
    grok.layer(MySkin)

    def render(self):
        return "<p> This is the render method of the <b> Start </b> class </p>"
    
