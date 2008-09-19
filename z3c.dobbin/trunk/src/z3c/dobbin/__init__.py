from sqlalchemy import util
from monkey import wrap, PatchException

import types

# patch sqlalchemy.util.class_hierarchy to filter out old-style classes
# reference:
# http://groups.google.com/group/sqlalchemy/browse_thread/thread/97f81966830da19b#
try:
    @wrap(util.class_hierarchy,
          '02daa72fd6238e668a27fa11781b7b372548e910',
          '99edc891c7fab3b2e1c7838e3e51f4b146e81e46')
    def filtered_class_hierarchy(func, cls):
        hier = func(cls)
        return [cls for cls in hier if not isinstance(cls, types.ClassType)]

    util.class_hierarchy = filtered_class_hierarch
except PatchException:
    pass
