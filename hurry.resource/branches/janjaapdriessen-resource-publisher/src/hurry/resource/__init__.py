from hurry.resource.core import (Library,
                                 libraries,
                                 ResourceInclusion,
                                 GroupInclusion,
                                 NeededInclusions)

from hurry.resource.core import (sort_inclusions_topological,
                                 sort_inclusions_by_extension,
                                 generate_code)

from hurry.resource.core import (register_plugin,
                                 get_current_needed_inclusions)

publisher_signature = 'fanstatic'

devmode = False

def configure_devmode(enable=True):
    global devmode
    devmode = enable
