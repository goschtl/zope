##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

""" 
Resources registry for templates, styles etc.
"""

import os
from zope.interface import Interface, providedBy, implements

from ConfigParser import ConfigParser
from logger import LOG

# mapping interface -> resource name -> Resource instance
resources_registry = dict()


class Resource(dict):
    """ A resource is a simple data-structure (mapping) that
        contains a registered set of data (template, styles, etc.)
        for a given interface. Keys used so far:

        name - name of resource as defined in the INI file
        template_filename - path to template file
        description - textual description of the template
        styles - dict mapping style names to their full filenames
        for_converters - list of converter name as defined through zopyx.convert
        configuration_filename - full path of defining configuration file
    """

    def __getattr__(self, k, default=None):
        """ make dict keys available as attributes """

        if k in self.keys():
            return self[k]
        return super(Resource, self).__getattr__(k, default)


class ConfigurationError(Exception):
    pass

def registerResource(iface, configuration_filename):
    """ Parses a resources configuration with the following format
        and adds it to the resources_registry.

        [demo]
        description = demo demo demo
        template = demo_template.pt
        styles = demo1.css
                 demo2.css
        # or
        # styles = demo1.css, demo2.css
        for-converter = pdf-fop 
                        pdf-prince
    """

    configuration_filename = os.path.abspath(configuration_filename)
    if not os.path.exists(configuration_filename):
        raise ConfigurationError('Configuration file %s does not exist' % configuration_filename)

    if not issubclass(iface, Interface):
        raise ConfigurationError('"iface" parameter must be a subclass of '
                                 'zope.interface.Interface (found %s)' % iface.__class__)

    configuration_directory = os.path.dirname(configuration_filename)

    CP = ConfigParser()
    LOG.debug('Parsing %s' % configuration_filename)
    CP.read([configuration_filename])

    for section in CP.sections():
        for option in ('template', 'for-converter', 'styles', 'description'):
            if not CP.has_option(section, option):
                raise ConfigurationError('Configuration file %s has no option "%s" in section "%s"' % 
                                         (configuration_filename, option, section))

        description = CP.get(section, 'description')

        template = CP.get(section, 'template')
        template_filename = os.path.join(configuration_directory, template)
        if not os.path.exists(template_filename):
            raise ConfigurationError('Template %s does not exist' % template_filename)

        items = CP.get(section, 'styles')
        uses_comma = ',' in items
        items = items.split(uses_comma and ',' or '\n')
        styles = [item.strip() for item in items if item]
        styles2 = dict()
        for style in styles:
            style_filename = os.path.join(configuration_directory, style)
            if not os.path.exists(style_filename):
                raise ConfigurationError('Style %s does not exist' % style_filename)
            styles2[style] = style_filename

        items = CP.get(section, 'for-converter')
        uses_comma = ',' in items
        items = items.split(uses_comma and ',' or '\n')
        converters = [item.strip() for item in items if item]
        for converter in converters :
            pass

    if not resources_registry.has_key(iface):
        resources_registry[iface] = dict()
    if resources_registry[iface].has_key(section):
        raise ConfigurationError('Section "%s" of configuration file %s is already registered' % 
                                 (section, configuration_filename))

    # creating and registering a new Resource instance for the given interface
    r = Resource(name=section,
                 template_filename=template_filename,
                 description=description,
                 styles=styles2,
                 for_converters=converters,
                 configuration_filename=configuration_filename)
    resources_registry[iface][section] = r
    LOG.debug('Adding configuration: %s' % r)


def getResourcesFor(context, name=None):
    """ Returns all resources for a given object based on the 
        interfaces they implement. A single resource can be picked
        by name.
    """

    all_registered_ifaces = resources_registry.keys()
    candidates = list()
    for iface in providedBy(context).flattened():
        if iface in all_registered_ifaces:
            candidates.append(resources_registry[iface])

    if name:
        for item in candidates:
            for k, v in item.items():
                if k == name:
                    return v
        raise ValueError('No resources with name "%s" registered' % name)
   
    return candidates

if __name__ == '__main__':
    import sys
    class ISample(Interface):
        pass
    registerResource(ISample, sys.argv[1])
    print resources_registry
    
    print getResourcesFor(object)

    class Sample(object):
        implements(ISample)
    print getResourcesFor(Sample())



