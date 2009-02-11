

class StageList(object):
    implements(IStageList)

    def __init__(self, names):
        self.names = names

    def adapt(self, request):
        """Called by adapter lookup"""
        return self


class MarkerRequest(object):
    """A marker object that claims to provide a request type.

    This is used for adapter lookup.
    """

    __slots__ = ('__provides__',)

    def __init__(self, request_type):
        request_type.directlyProvidedBy(self)


class Pipeline(object):
    implements(IWSGIApplication)

    def __init__(self, request_type):
        self.app = None
        self.request_type = request_type

    def adapt(self, request):
        """Called by adapter lookup"""
        app = self.app
        if app is None:
            self.app = app = self.make_app()
        return app

    def make_app(self):
        marker_req = MarkerRequest(self.request_type)
        stage_list = IStageList(marker_req)
        names = list(stage_list.names)  # make a copy
        # The last name in the list is an application.
        name = names.pop()
        app = IWSGIApplication(marker_req, name=name)
        while names:
            # The rest of the names are middleware.
            name = names.pop()
            app = getMultiAdapter(
                (app, marker_req), IWSGIApplication, name=name)
        return app
