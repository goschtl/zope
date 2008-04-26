from martian.directive import MultipleTimesDirective
from martian.directive import BaseTextDirective,
from martian.directive import SingleValue
from martian.directive import ClassDirectiveContext

class RequireDirective(BaseTextDirective, SingleValue, MultipleTimesDirective):

    def store(self, frame, value):
        super(RequireDirective, self).store(frame, value)
        values = frame.f_locals.get(self.local_name, [])

        # grok.require can be used both as a class-level directive and
        # as a decorator for methods.  Therefore we return a decorator
        # here, which may be used for methods, or simply ignored when
        # used as a directive.
        def decorator(func):
            permission = values.pop()
            func.__grok_require__ = permission
            return func
        return decorator
    
require = RequireDirective('grok.require', ClassDirectiveContext()) 
