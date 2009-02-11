
"""Creates the WSGI pipeline configured by ZCML and the component architecture.


"""

from zope.publisher.interfaces import IWSGIApplication

standard_stages = []  # set by pipeline:stages directive

def make_app(configuration, stages=standard_stages):
    stages = list(stages)  # make a copy
    name = stages.pop()
    app = build_stage(None, name, configuration)
    while stages:
        name = stages.pop()
        app = build_stage(app, name, configuration)
    return app

def build_stage(app, name, configuration):
    res = None
    # look for an app that requires the configuration
    if app is None:
        res = IWSGIApplication(configuration, name=name, default=None)
    else:
        res = IWSGIApplication(app, configuration, name=name, default=None)
    if res is not None:
        return res
    # look for an app that requires no configuration
    if app is None:
        res = IWSGIApplication(name=name)
    else:
        res = IWSGIApplication(app, name=name)
    return res
