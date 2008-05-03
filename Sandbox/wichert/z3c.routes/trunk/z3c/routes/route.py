import re
from zope.dottedname.resolve import resolve
from zope.interface import implements
from z3c.routes.interfaces import IRoute

class Route(object):
    implements(IRoute)

    variable_matcher = re.compile(r"/:([^/]+)")

    def __init__(self, route, factory, **kwargs):
        self.route=route
        self.variables=kwargs

        if isinstance(factory, basestring):
            self.factory=resolve(factory)
        else:
            self.factory=factory

        if not callable(self.factory):
            raise TypeError("Factory has to be a (dotted name of a) callable")

        self._compile()


    def _compile(self):
        matcher=self.variable_matcher.sub(r"/(?P<\1>[^/]+)", self.route)
        matcher+=r"\b"
        self._matcher=re.compile(matcher)


    def match(self, path, request):
        matches=self._matcher.match(path)
        if matches is None:
            return False

        variables=self.variables.copy()
        variables.update(matches.groupdict())
        request.annotations["z3c.routes.variables"]=variables
        request.annotations["z3c.routes.path"]=path[:matches.end()]
        return True


    def execute(self, request):
        parts=filter(None, request.annotations["z3c.routes.path"].split("/"))
        request.setTraversalStack(request.getTraversalStack()[len(parts)-1:])

        return self.factory(**request.annotations["z3c.routes.variables"])


