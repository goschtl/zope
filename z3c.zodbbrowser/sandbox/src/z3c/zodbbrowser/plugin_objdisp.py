# -*- coding: UTF-8 -*-

#plugin for object display
#currently this is just for fun

from wax import *

from z3c.zodbbrowser.bases import BaseObjDisplayPlugin

class dictDispPlugin(BaseObjDisplayPlugin):
    title = u'dict details'
    
    def onClick(self):
        dlg = MessageDialog(self.form, "A message", "dict details")
        dlg.ShowModal()
        dlg.Destroy()

def main(PluginRegistry):
    PluginRegistry['obj_display'].append(('dict',dictDispPlugin))