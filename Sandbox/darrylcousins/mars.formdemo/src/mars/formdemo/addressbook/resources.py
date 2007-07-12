import zope.interface
from zope.viewlet.viewlet import CSSViewlet, JavaScriptViewlet

import grok

import mars.resource
import mars.viewlet
import mars.layer
from mars.formdemo.layer import IDemoBrowserLayer
from mars.formdemo.skin import skin
from mars.formdemo.addressbook.addressbook import AddressBook

mars.layer.layer(IDemoBrowserLayer)

## CSS resources
class AddressbookResource(mars.resource.ResourceFactory):
    """File resource"""
    grok.name('addressbook.css')
    mars.resource.file('addressbook.css')

AddressbookCSSViewlet = CSSViewlet('addressbook.css')
class FormAddressbookCSSViewlet(mars.viewlet.SimpleViewlet, AddressbookCSSViewlet):
    """css viewlet"""
    weight = 1000
    grok.name('addressbook.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.view(AddressBook)
    mars.viewlet.manager(skin.CSSManager)

## Javascript resources
class TextShadowResource(mars.resource.ResourceFactory):
    """File resource"""
    grok.name('text-shadow.js')
    mars.resource.file('text-shadow.js')

TextShadowViewlet = JavaScriptViewlet('text-shadow.js')
class FormTextShadowJSViewlet(mars.viewlet.SimpleViewlet, TextShadowViewlet):
    """css viewlet"""
    grok.name('addressbook.css')
    grok.context(zope.interface.Interface)
    mars.viewlet.view(AddressBook)
    mars.viewlet.manager(skin.JavaScriptManager)

class NoErrorWidget(mars.macro.MacroFactory):
 """Name defaults to factory.__name__, 'navigation'"""
 grok.name('widget-noerror-row')
 grok.template('form-macros.pt') # required
 grok.context(zope.interface.Interface) # required if no module context 

