from hurry.resource.core import (Library,
                                 libraries,
                                 ResourceInclusion,
                                 GroupInclusion,
                                 NeededInclusions)

from hurry.resource.core import (mode, bottom, rollup,
                                 render, render_topbottom, render_into_html,
                                 render_topbottom_into_html)

from hurry.resource.core import (sort_inclusions_topological,
                                 sort_inclusions_by_extension,
                                 generate_code)

from hurry.resource.core import (register_plugin,
                                 get_current_needed_inclusions)

hashing = True

def configure_hashing(enable=True):
    global hashing
    hashing = enable

publisher_signature = ':hash:'

devmode = False

def configure_devmode(enable=True):
    global devmode
    devmode = enable
