from zope import component
from zope import interface
import interfaces
from zope.app.container.interfaces import IObjectAddedEvent
from z3c.configurator import configurator

@component.adapter(interfaces.IConfigurableSite,
                   IObjectAddedEvent)
def applyConfigurators(obj, event):
    cfg = interfaces.ISiteConfig(obj).config
    configurators = cfg.get('configurators')
    if configurators is not None:
        configurator.configure(obj, configurators, names=configurators.keys(),
                               useNameSpaces=True)
