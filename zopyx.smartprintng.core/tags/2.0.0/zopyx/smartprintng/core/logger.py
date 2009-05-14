##########################################################################
# zopyx.smartprintng.core - High-quality export of Zope content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import logging


try:
    import zLOG
    LOG = logging.getLogger('smartprintng')
except ImportError:
    LOG = logging.getLogger()
    hdl = logging.StreamHandler()
    fmt = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    hdl.setFormatter(fmt)
    LOG.addHandler(hdl)
    level = os.environ.has_key('SMARTPRINTNG_DEBUG') and logging.DEBUG or logging.INFO
    LOG.setLevel(level)


if __name__ == '__main__':
    LOG.debug('test')
    LOG.info('test')
    LOG.warn('test')
    LOG.error('test')
