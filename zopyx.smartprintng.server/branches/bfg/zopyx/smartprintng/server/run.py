from repoze.bfg.router import make_app

def app(global_config, **kw):
    """ This function returns a repoze.bfg.router.Router object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""
    # paster app config callback
    from zopyx.smartprintng.server.models import get_root
    import zopyx.smartprintng.server
    return make_app(get_root, zopyx.smartprintng.server, options=kw)

