from martian.directive import (OnceDirective, SingleTextDirective,
                               SingleValue,
                               ClassDirectiveContext)

class RdbKeyDirective(SingleTextDirective, OnceDirective):
    """
    Directive that accepts a string to be used as the lookup key
    """
    pass

key = RdbKeyDirective('rdb.key', ClassDirectiveContext())
