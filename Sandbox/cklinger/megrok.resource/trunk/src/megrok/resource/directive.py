import martian
from martian import util
from martian.error import GrokImportError


def default_list(factory, module=None, **data):
    return []


def default_library_name(factory, module=None, **data):
    return factory.__name__.lower()


class inclusion(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE

    def factory(self, name, file, depends=[], bottom=False):
        return (name, file, depends, bottom)


class include(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    
    def factory(self, value, name=None, bottom=False):
        return (value, name, bottom)
