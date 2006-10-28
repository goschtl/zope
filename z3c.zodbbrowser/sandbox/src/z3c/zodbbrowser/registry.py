# -*- coding: UTF-8 -*-

#plugin registry and support methods

import imp
import sys
import os
import glob

#plugin registry
PluginRegistry = {}

#object inspector plugin registry
#format is: [(importance or specificity, pluginClass)]
#importance is an integer, plugins get checked in the order of this
#so AnyObjectTypePlugin should be sys.maxint
#the more specific the plugin is the less this number should be
PluginRegistry['object']=[]

#data source plugin registry
#format is: [("plugin title", "extension", pluginClass)]
#contents will be put on the menu File/Open <plugin title>
PluginRegistry['source']=[]

#data source display plugin registry
#format is: {"plugin name":pluginClass}
#the data source plugin can define which displays it 'likes'
PluginRegistry['db_display']={}

#object display plugin registry
#these plugins are checked when the user right-clicks in the tree? on any 
#object plugins matching by type will be displayed in a shortcut menu
#format is: [("object type", pluginClass)]
#object type can be "*", then the plugin applies for all types
#with the "*" a kind of 'open new window from here...' could be implemented
PluginRegistry['obj_display']=[]

def getObjectPlugin(text, obj):
    u"""get one matching plugin for the object
    checks lowest priority first"""
    for prio, plugin in PluginRegistry['object']:
        plg = plugin(obj)
        if plg.match(text):
            return plg
    
    return None

def getSourcePlugins():
    u"""return source plugin list"""
    return PluginRegistry['source']

def getDBDisplayPlugins(types):
    u"""get display plugins according to types list"""
    matches = []
    for type in types:
        try:
            matches.append(PluginRegistry['db_display'][type])
        except KeyError:
            print "No plugin found for display '%s'" % type
    return matches

def getDisplayPlugins(objtype):
    u"""get object display plugins for an object type"""
    matches = [pluginklass
               for type, pluginklass in PluginRegistry['obj_display']
               if (type == objtype) or (type == '*')]
    return matches

def impmain(fname):
    u"""import main from a given .py file"""
    mname = os.path.splitext(fname)[0]
    mpath, mname = os.path.split(mname)
    oname = 'main'
        
    try:
        x=imp.find_module(mname, [mpath])
        try:
            mod=imp.load_module('plugin1',x[0],x[1],x[2])
        finally:
            x[0].close()
    except ImportError, v:
        raise ValueError(
            "Couldn't import %s, %s" % (mname, v)), None, sys.exc_info()[2]
    
    try:
        obj = getattr(mod, oname)
        return obj
    except AttributeError:
        # No such name, maybe it's a module that we still need to import
        #try:
        #    return __import__(mname+'.'+oname, *_import_chickens)
        #except ImportError:
        #
        # We need to try to figure out what module the import
        # error is complaining about.  If the import failed
        # due to a failure to import some other module
        # imported by the module we are importing, we want to
        # know it. Unfortunately, the value of the import
        # error is just a string error message. :( We can't
        # pull it apart directly to see what module couldn't
        # be imported. The only thing we can really do is to
        # try to "screen scrape" the error message:

        if str(sys.exc_info()[1]).find(oname) < 0:
            # There seems to have been an error further down,
            # so reraise the exception so as not to hide it.
            raise

        raise ValueError(
            "ImportError: Module %s has no global %s" % (mname, oname)) 

def installplugins():
    u"""import and start the main() of each plugin_*.py
    in the folder of our source
    these should register/can register any plugin
    through the passed PluginRegistry parameter"""
    here = os.path.dirname(os.path.abspath(__file__))
    #here = os.path.abspath(os.path.dirname(sys.argv[0]))
    plugins = glob.glob(os.path.join(here, "plugin*.py"))
    
    for plg in plugins:
        plgmain = impmain(plg)
        plgmain(PluginRegistry)
    
    PluginRegistry['object'].sort()