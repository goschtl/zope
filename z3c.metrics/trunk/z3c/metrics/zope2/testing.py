from zope.testing import cleanup

import DateTime

def freezeATDefaultDate(datetime_, cls, field_name='creation_date'):
    field = cls.schema[field_name]

    # If this is the first time we've touched the field, keep the
    # original default method around to restore on cleanup
    if not hasattr(field, 'default_method_orig'):
        field.default_method_orig = field.default_method
        def cleanUp():
            field.default_method = field.default_method_orig
            del field.default_method_orig
        cleanup.addCleanUp(cleanUp)

    field.default_method = lambda: datetime_

def freezeATDefaultDates(datetime_, classes,
                         field_name='creation_date'):
    for cls in classes:
        freezeATDefaultDate(datetime_, cls, field_name)

class FrozenDateTime(DateTime.DateTime):

    def __init__(self, *args, **kw):
        if not (args or kw):
            return DateTime.DateTime.__init__(self, self._frozen)
        return DateTime.DateTime.__init__(self, *args, **kw)

def freezeDateTime(datetime_, module):
    def cleanUp():
        if hasattr(module.DateTime, 'orig'):
            module.DateTime = module.DateTime.orig
    cleanUp()

    FrozenDateTime.orig = module.DateTime
    FrozenDateTime._frozen = datetime_
    module.DateTime = FrozenDateTime

    cleanup.addCleanUp(cleanUp)
