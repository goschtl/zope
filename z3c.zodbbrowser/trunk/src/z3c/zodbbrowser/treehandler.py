# -*- coding: UTF-8 -*-

#tree handler for plugin_tree

from wax import *

from z3c.zodbbrowser.registry import getObjectPlugin, getDisplayPlugins
from z3c.zodbbrowser.utils import *

class baseHandler(object):
    """ """
    
    expandable = False
    
    def __init__(self, context, text, form):
        self.context = context
        self.form = form
        self.text = text
        self.plugin = getObjectPlugin(text, context)
    
    def onRightClick(self):
        type = self.plugin.getType()
        plugins = getDisplayPlugins(type)
        
        if plugins:
            menu = Menu(self.form)
            
            for pluginklass in plugins:
                plugin = pluginklass(self.context, self.form)
                # these entries are always present
                menu.Append(plugin.getTitle(), curry(self.onPopupMenu, plugin))
    
            self.form.PopupMenu(menu)
            #menu.Destroy()  # ...why?
            #core.wx.GetApp().ProcessIdle()   # ...?
    
    def onPopupMenu(self, itemplugin, event):
        print itemplugin.getTitle()
        itemplugin.onClick()

class leafHandler(baseHandler):
    #def __init__(self, context):
    #    self.context = context
    
    def onSelected(self):
        #print "leaf selected"
        props = self.plugin.getProps()
        out = ["%s (%s) = %s" % (prop.text, prop.type, safe_str(prop.data))
               for prop in props.getAll()]
        
        typ = safe_str(type(self.context))
        id = safe_str(self.context)
        doc=''
        try:
            doc = self.context.__doc__
        except:
            pass
        head = """Type: %s
-------------
ID: %s
-------------
__doc__: %s
=============
""" % (typ, id, doc)
        
        data={'text':head+'\n'.join(out)}
        self.form.setProps(data)
    
    #def onRightClick(self):
    #    print "leaf onRightClick"
    
    def onExpanded(self):
        #print "leaf expanded"
        pass
    
    def getChildren(self):
        return None

class containerHandler(leafHandler):
    expandable = True
    
    #def __init__(self, context):
    #    self.context = context
    
    #def onSelected(self):
    #    print "container selected"
    #    props = self.plugin.getProps(self.context)
    #    out = ["%s (%s) = %s" % (prop.text, prop.type, safe_str(prop.data)) for prop in props.getAll()]
    #        
    #    data={'text':'\n'.join(out)}
    #    self.form.setProps(data)
    
    #def onRightClick(self):
    #    print "container onRightClick"
    
    def onExpanded(self):
        #print "container expanded"
        pass
    
    def getChildren(self):
        items = []
        kids = self.plugin.getChildren()
        
        props = self.plugin.getProps()
        for prop in props.getAll():
            if prop.expandable:
                kids.addLL(prop)
        
        for kid in kids.getAll():
            if kid.expandable:
                #expandable
                handler = containerHandler(kid.data, kid.text, self.form)
            else:
                handler = leafHandler(kid.data, kid.text, self.form)
            
            items.append(("%s (%s)" %(kid.text, kid.type), handler))
                
        return items

class rootHandler(containerHandler):
    expandable = True
    
    #def __init__(self, context, form):
    #    self.context = context
    #    self.form = form
    
    def onSelected(self):
        #print "root selected"
        data={'text':''}
        self.form.setProps(data)
    
    #def onRightClick(self):
    #    print "root onRightClick"
    
    def onExpanded(self):
        #print "root expanded"
        pass
    
    #def getChildren(self):
    #    items = [(key, containerHandler(obj)) for key,obj in LogicRegistry().items()]
    #    return items
