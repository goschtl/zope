import os
from pkg_resources import iter_entry_points
from pkg_resources import resource_filename

def find_plugins(dotted_name):
    plugins = []
    for ep in iter_entry_points('z3c.autoinclude.plugin'):
        if ep.name == dotted_name:
            plugins.append(ep.module_name)
    return plugins

def zcml_to_include(dotted_name, zcmlgroups=None):
    if zcmlgroups is None:
        zcmlgroups = ('meta.zcml', 'configure.zcml', 'overrides.zcml')
    
    includable_info = []

    for zcmlgroup in zcmlgroups:
        filename = resource_filename(dotted_name, zcmlgroup)
        if os.path.isfile(filename):
            includable_info.append(zcmlgroup)
    return includable_info

def plugins_to_include(platform_dottedname, zcmlgroups=None):
    includable_info = {}

    for plugin_dottedname in find_plugins(platform_dottedname):
        groups = zcml_to_include(plugin_dottedname, zcmlgroups)
        for group in groups:
            includable_info.setdefault(group, []).append(plugin_dottedname)
    return includable_info
