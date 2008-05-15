import martian
from martian.error import GrokError

import megrok.rdb
from megrok.rdb import directive

class ContainerGrokker(martian.ClassGrokker):
    component_class = megrok.rdb.Container

    def grok(self, name, factory, module_info, config, **kw):
        rdb_key = directive.key.get(factory)
        if rdb_key and hasattr(factory, 'keyfunc'):
            raise GrokError(
                "It is not allowed to specify a custom 'keyfunc' method "
                "for rdb.Container %r, when a rdb.key directive has also "
                "been given." % factory, factory)
        return True
