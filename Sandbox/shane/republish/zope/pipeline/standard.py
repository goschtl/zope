
"""Creates a standard Zope WSGI publishing pipeline."""

from zope.pipeline.call import Caller

standard_pipeline = (
    # RequestProfiler,
    # CodeFreshnessChecker,
    # Multiprocessor,
    # ComponentConfigurator,
    # DetailedTracebackGenerator,
    RequestLogger,
    RequestCreator,         # also sets locale (?)
    DatabaseOpener,
    TransactionController,  # includes retry logic and annotation
    choose_traverser,       # complex or simple traversal based on zope.conf
    AppErrorHandler,
    Caller
)

def make_app(zope_conf, pipeline=standard_pipeline):
    p = list(pipeline)
    factory = p.pop()
    app = factory(zope_conf)
    while p:
        factory, kw = p.pop()
        app = factory(app, zope_conf)
    return app
