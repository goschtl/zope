##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
__docformat__ = "reStructuredText"

import ConfigParser
import logging
import os

__CONFIG_SECTION__ = 'zc.testbrowser'
__CONFIGFILE__ = os.path.expanduser('~/.zc.testbrowser.cfg')

def get_ztb_config(config=None):
    """If config is a str, just try to read the __CONFIG_SECTION__
    in config and return it.
    Ensure also that config is a dict.
    """
    if not config:
        config = ''
    if isinstance(config, str):
        configreader = ConfigParser.ConfigParser()
        # only generate a config file if we want to use proxies
        if not config:
            config = __CONFIGFILE__
        if config and not os.path.exists(config):
            logging.getLogger(__name__).debug('Generating config file for '
                                              'storing your %s informaton '
                                              'in %s.' % (config, __name__))
            configreader.write(config)
            configreader.add_section(__CONFIG_SECTION__)
            configreader.set(__CONFIG_SECTION__, 'proxies', '')
            configreader.write(open(config, 'w'))
        configreader.read(config)
        config = configreader._sections.get(__CONFIG_SECTION__, {})
    assert isinstance(config, dict)
    return config

def which(program, environ=None, key = 'PATH', split = ':'):
    if not environ:
        environ = os.environ
    PATH=environ.get(key, '').split(split)
    fp = None
    if '/' in program:
        fp = os.path.abspath(program)
    if not fp:
        for entry in PATH:
            fp = os.path.abspath(os.path.join(entry, program))
            if os.path.exists(fp):
                break
    if os.path.exists(fp):
        return fp
    raise IOError('Program not fond: %s in %s ' % (program, PATH))

