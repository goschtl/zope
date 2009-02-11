

def passthrough(app):
    """A passthrough application.

    Use this to skip a pipeline step.  Register this function
    as the middleware factory for a step you don't want to use.
    The step will be eliminated even from application stack traces.
    """
    return app
