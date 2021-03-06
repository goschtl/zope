##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from repoze.bfg.router import make_app
import mail_util
from views import have_authentication

def app(global_config, **kw):
    """ This function returns a repoze.bfg.router.Router object.  It
    is usually called by the PasteDeploy framework during ``paster
    serve``"""

    # paster app config callback
    from zopyx.smartprintng.server.models import get_root
    import zopyx.smartprintng.server
    from models import root
    from logger import LOG

    if 'mail_config' in global_config:
        mail_config = os.path.abspath(global_config['mail_config'])
        os.environ['EMAIL_CONFIG'] = mail_config
        config = mail_util.setupMailer()
        LOG.info('Using email configuration at %s' % mail_config)
        LOG.info(config)
    LOG.info('SmartPrintNG server started')
    LOG.info('Temp directory: %s' % root.temp_directory)
    LOG.info('Spool directory: %s' % root.spool_directory)
    if have_authentication:
        LOG.info('Authentication module found - server requires authentication')
    else:
        LOG.info('No auth module found - serving for anonymous')

    return make_app(get_root, zopyx.smartprintng.server, options=kw)

