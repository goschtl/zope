""" GenericSetup export / import support for PluginRegistry.

$Id$
"""
from Persistence import PersistentMapping

from Products.GenericSetup.utils import ExportConfiguratorBase
from Products.GenericSetup.utils import ImportConfiguratorBase
from Products.GenericSetup.utils import _getDottedName
from Products.GenericSetup.utils import _resolveDottedName
from Products.GenericSetup.utils import CONVERTER
from Products.GenericSetup.utils import DEFAULT
from Products.GenericSetup.utils import KEY
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from interfaces.plugins import IPluginRegistry

def _providedBy(obj, iface):
    try:
        return iface.providedBy(obj)
    except AttributeError:
        return iface.isImplementedBy(obj) # Z2 interfaces

_FILENAME = 'pluginregistry.xml'

def _getRegistry(site):
    registries = [x for x in site.objectValues()
                    if _providedBy(x, IPluginRegistry)]

    if len(registries) < 1:
        raise ValueError, 'No plugin registries'

    if len(registries) > 1:
        raise ValueError, 'Too many plugin registries'

    return registries[0]

def exportPluginRegistry(context):
    """ Export plugin registry as an XML file.
    """
    registry = _getRegistry(context.getSite())
    pre = PluginRegistryExporter(registry).__of__(registry)
    xml = pre.generateXML()
    context.writeDataFile(_FILENAME, xml, 'text/xml')

    return 'Plugin registry exported.'

def importPluginRegistry(context):
    """ Import plugin registry from an XML file.
    """
    registry = _getRegistry(context.getSite())
    encoding = context.getEncoding()

    xml = context.readDataFile(_FILENAME)
    if xml is None:
        return 'Site properties: Nothing to import.'

    if context.shouldPurge():

        registry._plugin_types = []
        registry._plugin_type_info = PersistentMapping()
        registry._plugins = PersistentMapping()

    pir = PluginRegistryImporter(registry, encoding)
    reg_info = pir.parseXML(xml)

    for info in reg_info['plugin_types']:
        iface = _resolveDottedName(info['interface'])
        registry._plugin_types.append(iface)
        registry._plugin_type_info[iface] = {'id': info['id'],
                                             'title': info['title'],
                                             'description': info['description'],
                                            }
        registry._plugins[iface] = tuple([x['id'] for x in info['plugins']])

    return 'Plugin registry imported.'

class PluginRegistryExporter(ExportConfiguratorBase):

    def __init__(self, context, encoding=None):
        ExportConfiguratorBase.__init__(self, None, encoding)
        self.context = context

    def _getExportTemplate(self):
        return PageTemplateFile('xml/pirExport.xml', globals())

    def listPluginTypes(self):
        for info in self.context.listPluginTypeInfo():
            iface = info['interface']
            info['interface'] = _getDottedName(iface)
            info['plugins'] = self.context.listPluginIds(iface)
            yield info

class PluginRegistryImporter(ImportConfiguratorBase):

    def __init__(self, context, encoding=None):
        ImportConfiguratorBase.__init__(self, None, encoding)
        self.context = context

    def _getImportMapping(self):

        return {
          'plugin-registry':
            {'plugin-type': {KEY: 'plugin_types', DEFAULT: ()},
            },
          'plugin-type':
            {'id':          {KEY: 'id'},
             'interface':   {KEY: 'interface'},
             'title':       {KEY: 'title'},
             'description': {KEY: 'description'},
             'plugin':      {KEY: 'plugins', DEFAULT: ()}
            },
          'plugin':
            {'id':          {KEY: 'id'},
            },
         }
