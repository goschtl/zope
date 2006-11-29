# -*- coding: UTF-8 -*-

#plugin registry and support methods

import imp
import sys
import os

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


def installplugins():
    """Import and register all plugins.

    Plugins are all "plugin_*" modules from the same package as this registry.

    Plugins are registered by calling their register_plugin() method with the
    registry as the parameter.

    """
    base_package = ".".join(__name__.split('.')[:-1])

    base_dir = os.path.dirname(os.path.realpath(__file__))

    plugin_names = []
    for name in os.listdir(base_dir):
        if not name.startswith('plugin_'):
            continue
        if not name.endswith('.py'):
            # XXX This is a huge simplification, but this "plugin" system
            # is crude anyway.
            continue
        plugin_names.append(name[:-3])

    plugin_parent = __import__(base_package, globals(), locals(), plugin_names)
    for plugin_name in plugin_names:
        plugin = getattr(plugin_parent, plugin_name)
        plugin.register(PluginRegistry)

    # Registered object plugins need to be sorted by their
    # priority for searching. Ideally this should be using a BTree
    # with the priority as a key.
    PluginRegistry['object'].sort()
