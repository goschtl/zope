""" GenericSetup product initialization.

$Id: __init__.py,v 1.1.1.1 2005/08/08 19:38:37 tseaver Exp $
"""

genericsetup_globals = globals()

from AccessControl import ModuleSecurityInfo

from interfaces import BASE
from interfaces import EXTENSION
from permissions import ManagePortal
from registry import _profile_registry as profile_registry

security = ModuleSecurityInfo('Products.GenericSetup')
security.declareProtected(ManagePortal, 'profile_registry')

def initialize(context):

    import tool

    context.registerClass(tool.SetupTool,
                          constructors=(#tool.addSetupToolForm,
                                        tool.addSetupTool,
                                        ),
                          permissions=(ManagePortal,),
                          interfaces=None,
                          icon='www/tool.png',
                         )
