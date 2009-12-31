import os
import zope.app.wsgi

def application_factory(global_conf, conf='zope.conf'):
    zope_conf = os.path.join(global_conf['here'], conf)
    return zope.app.wsgi.getWSGIApplication(zope_conf)
