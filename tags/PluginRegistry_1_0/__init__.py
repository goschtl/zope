""" PluginRegistry product initialization.

$Id$
"""

from utils import allTests

import PluginRegistry

def initialize(context):

    context.registerClass( PluginRegistry.PluginRegistry
                         , constructors=[ ( 'Dummy', lambda: None ) ]
                         , visibility=None
                         , icon='www/PluginRegistry.png'
                         )

