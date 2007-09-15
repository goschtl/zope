import os
import code
import zope.app.wsgi
import zope.app.debug

def application_factory(global_conf, conf='zope.conf'):
    zope_conf = os.path.join(global_conf['here'], conf)
    return zope.app.wsgi.getWSGIApplication(zope_conf)

def interactive_debug_prompt(zope_conf='zope.conf'):
    db = zope.app.wsgi.config(zope_conf)
    debugger = zope.app.debug.Debugger.fromDatabase(db)
    # Invoke an interactive interpreter shell
    banner = ("Welcome to the interactive debug prompt.\n"
              "The 'root' variable contains the ZODB root folder.\n"
              "The 'app' variable contains the Debugger, 'app.publish(path)' "
              "simulates a request.")
    code.interact(banner=banner, local={'debugger': debugger,
                                        'app':      debugger,
                                        'root':     debugger.root()})
