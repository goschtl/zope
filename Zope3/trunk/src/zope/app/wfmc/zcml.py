"""ZCML directives for defining privileges.

$Id: $
"""

import zope.interface
import zope.schema
import zope.configuration.fields
import zope.component

from zope.app import zapi
from zope import wfmc
from zope.wfmc import xpdl

class IdefineXpdl(zope.interface.Interface):

    file = zope.configuration.fields.MessageID(
        title=u"File Name",
        description=u"The name of the xpdl file to read.",
        )

    process = zope.configuration.fields.MessageID(
        title=u"Process Name",
        description=u"The name of the process to read.",
        )

    id = zope.configuration.fields.MessageID(
        title=u"ID",
        description=(u"The identifier to use for the process.  "
                     u"Defaults to the process name."),
        required=False,
        )

def createUtility(file, process, id, info=None):
    # XXX should I use info for something?
    package = xpdl.read(open(file))
    definition = package[process]
    definition.id = id

    zapi.getGlobalService('Utilities').provideUtility(
            wfmc.interfaces.IProcessDefinition, definition, definition.id)

def defineXpdl(_context, file, process, id=None):
    if not id:
        id = process

    _context.action(
        discriminator=('intranet:xpdl', id),
        callable=createUtility, 
        args=(file, process, id, _context.info),
        )
