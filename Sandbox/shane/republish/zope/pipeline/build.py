
"""Creates the WSGI pipeline configured by ZCML and the component architecture.


"""

from zope.publisher.interfaces import IWSGIApplication

configured_stages = []  # set by pipeline:stages directive

def make_app(configuration, stages=configured_stages):
    stages = list(stages)  # make a copy

    # the last stage name is the application
    name = stages.pop()
    app = IWSGIApplication(configuration, name=name, default=None)
    if app is None:
        app = IWSGIApplication(name=name)

    # the rest are middleware
    while stages:
        name = stages.pop()
        new_app = IWSGIApplication(app, configuration, name=name, default=None)
        if new_app is None:
            new_app = IWSGIApplication(app, name=name)
        app = new_app

    return app
