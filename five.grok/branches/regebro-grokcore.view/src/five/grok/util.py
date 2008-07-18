from martian.error import GrokError
from five import grok

def get_name_classname(factory):
    name = grok.name.get(factory)
    if not name:
        name = factory.__name__.lower()
    return name
