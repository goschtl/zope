"""WFMC metaconfigure

$Id: $
"""

import zope.interface
import zope.schema
import zope.configuration.fields
import zope.component

from zope.app import zapi
from zope import wfmc
from zope.wfmc import xpdl

def createUtility(file, process, id):
    package = xpdl.read(open(file))
    definition = package[process]
    definition.id = id

    zapi.getGlobalService('Utilities').provideUtility(
            wfmc.interfaces.IProcessDefinition, definition, id)

def defineXpdl(_context, file, process, id):
    _context.action(
        discriminator=('intranet:xpdl', id),
        callable=createUtility, 
        args=(file, process, id),
        )
