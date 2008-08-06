import grok
import zc.resourcelibrary
from megrok.resourcelibrary.directive import default_library_name

class ResourceLibrary(object):
    @classmethod
    def need(cls):
        name = grok.name.bind(get_default=default_library_name).get(cls)
        zc.resourcelibrary.need(name)
