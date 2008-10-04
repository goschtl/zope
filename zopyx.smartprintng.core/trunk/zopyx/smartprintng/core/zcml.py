#########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


"""'
ZCML directives for zopyx.smartprintng.core
"""

import os

from zope.interface import Interface
from zope.schema import TextLine 
import zope.configuration.fields

from logger import LOG

import resources
LOG = logging.getLogger()


class IResourcesDirectory(Interface):
    """ Used for specifying SmartPrintNG resources """

    directory = TextLine(
        title=u"Directory name",
        description=u'Directory path containing templates and styles for a given interface',
        default=u"",
        required=True)

    configname = TextLine(
        title=u"Configuration file name",
        description=u'Filename of configuration within the directory specified',
        default=u"resources.ini",
        required=False)

    interfaces = zope.configuration.fields.Tokens(
        title=u"For interfaces",
        description=u'Register the resource directory for the given interfaces',
        required=True,
        value_type=zope.configuration.fields.GlobalInterface())


def resourcesDirectory(_context, directory, configname, interfaces):

    # path of ZCML file
    zcml_filename = _context.info.file

    for iface in interfaces:
        configuration_filename = os.path.join(directory, configname)
        resources.registerResource(iface, configuration_filename)

