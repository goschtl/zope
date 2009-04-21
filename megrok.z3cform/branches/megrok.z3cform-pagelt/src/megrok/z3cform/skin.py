import grok                                                                                                       
import z3c.formui.interfaces

from z3c.form.interfaces import IFormLayer

class FormLayer(grok.IDefaultBrowserLayer, IFormLayer, z3c.formui.interfaces.IDivFormLayer):
    pass

