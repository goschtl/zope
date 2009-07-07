import grok
import z3c.formui.interfaces


from z3c.form.interfaces import IFormLayer


class FormLayer(grok.IDefaultBrowserLayer, 
                IFormLayer, 
                z3c.formui.interfaces.IDivFormLayer):
    """ A div -based layer for a z3c.forms"""


class TableLayer(grok.IDefaultBrowserLayer, 
                 IFormLayer, 
                 z3c.formui.interfaces.ITableFormLayer):
    """ A table -based layer for a z3c.forms"""
