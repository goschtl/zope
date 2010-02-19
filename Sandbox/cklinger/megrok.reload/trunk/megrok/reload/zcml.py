try:
    from zope.site.hooks import setSite
except ImportError:
    from zope.app.component.hooks import setSite

from zope.component import getGlobalSiteManager
from zope.testing import cleanup

import fivezcml

CORE_CLEANUPS = frozenset([
    'zope.app.apidoc.classregistry',
    'zope.app.component.hooks',
    'zope.app.security.principalregistry',
    'zope.app.schema.vocabulary',
    'zope.component.globalregistry',
    'zope.schema.vocabulary',
    'zope.security.management',
    'zope.security.checker',
    'zope.site.hooks',
])


def cleanups():
    registered = [c[0] for c in cleanup._cleanups]
    functions = []
    for r in registered:
        if r.__module__ not in CORE_CLEANUPS:
            functions.append(r)
    return functions

import martian
def reload_zcml():
    #from grokcore.component.zcml import 

    def resetBootstrap():
        # we need to make sure that the grokker registry is clean again
        the_module_grokker.clear()
    from zope.testing.cleanup import addCleanUp
    addCleanUp(resetBootstrap)

    the_multi_grokker = martian.MetaMultiGrokker()
    the_module_grokker = martian.ModuleGrokker(the_multi_grokker)

    return
    gsm = getGlobalSiteManager()
    old_gsm_dict = gsm.__dict__.copy()
    try:
        setSite(None)
        gsm.__init__(gsm.__name__)
        # Clean up
        for clean in cleanups():
            clean()
        # Reload all ZCML
        import pdb;pdb.set_trace()
        fivezcml._initialized = False
        fivezcml._context._seen_files.clear()
        fivezcml.load_site()
    except Exception, e:
        gsm.__init__(gsm.__name__)
        gsm.__dict__.clear()
        gsm.__dict__.update(old_gsm_dict)
        raise e
