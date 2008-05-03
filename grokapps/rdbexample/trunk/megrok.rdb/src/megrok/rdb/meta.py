import martian
from martian.error import GrokError

import megrok.rdb

class ContainerGrokker(martian.ClassGrokker):
    component_class = megrok.rdb.Container

    def grok(self, name, factory, module_info, config, **kw):
        if hasattr(factory, 'keyfunc') and hasattr(factory, '__rdb_key__'):
            raise GrokError(
                "It is not allowed to specify a custom 'keyfunc' method "
                "for rdb.Container %r, when a rdb.key directive has also "
                "been given." % factory, factory)
        return True
