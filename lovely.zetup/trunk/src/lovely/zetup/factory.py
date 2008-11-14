##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
import os.path
from config import Config
from app import Application
from zope import component

_app = None
_configPath = None

def app_factory(gcfg, cfg=None, logging=True):

    """initializer for past based setups

    A config path is required.
    >>> app_factory({})
    Traceback (most recent call last):
    ...
    ValueError: Missing config path None

    And it has to exist.
    >>> testing = os.path.join(os.path.dirname(__file__), 'testing', 'xy')
    >>> app_factory({'__file__':testing}, cfg='notthere.py')
    Traceback (most recent call last):
    ...
    ValueError: Config file not found '.../notthere.py'
    >>> app = app_factory({'__file__':testing}, cfg='testing.py')
    20...

    Called twice the app is the same.
    >>> app_factory({'__file__':testing}, cfg='testing.py') is app
    True

    We can only run one config at a time.
    >>> app_factory({'__file__':testing}, cfg='paste.ini')
    Traceback (most recent call last):
    ...
    RuntimeError: There is already another config running '.../testing.py'
    """
    if cfg is None:
        raise ValueError, "Missing config path %r" % cfg
    global _app, _configPath
    cfgFile = os.path.join(os.path.dirname(gcfg['__file__']), cfg)
    if _configPath is not None and _configPath != cfgFile:
        raise RuntimeError, "There is already another config" \
              +" running %r" % _configPath
    if not os.path.isfile(cfgFile):
        raise ValueError, "Config file not found %r" % cfgFile
    _configPath = cfgFile
    if _app is not None:
        return _app
    logging = logging not in ("0", "no", "false", "off")
    cfg = Config(cfgFile, withLogging=logging)
    component.provideUtility(cfg)
    _app = Application()
    return _app

def reset():
    global _app, _configPath
    _app = None
    _configPath = None

