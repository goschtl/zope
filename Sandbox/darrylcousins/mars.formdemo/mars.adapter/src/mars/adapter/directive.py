from martian.directive import (OnceDirective,
                               SingleValue,
                               ClassDirectiveContext)

class MethodDirective(SingleValue, OnceDirective):
    """
    Directive that only accepts factories??
    """

# FIXME
    def check_arguments(self, value):
        return True
        #if not (IInterface.providedBy(value) or util.isclass(value)):
        #    raise GrokImportError("You can only pass classes or interfaces to "
        #                          "%s." % self.name)

factory = MethodDirective('mars.adapter.factory',
                                 ClassDirectiveContext())
