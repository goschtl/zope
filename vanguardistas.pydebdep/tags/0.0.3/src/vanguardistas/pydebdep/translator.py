##############################################################################
#
# Copyright (c) 2008 Vanguardistas and Contributors.
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
import os
import logging
from subprocess import call

_marker = object()
_here = os.path.dirname(__file__)

class PackageNameTranslator:
    """
        >>> trans = PackageNameTranslator(source_egg_map={'somesource': 'someegg'})

    Try a default translation:

        >>> trans.egg_to_source('egg')
        'python-egg'

    A globally set translation:

        >>> trans.egg_to_source('PIL')
        'python-imaging'
        >>> trans.source_to_egg('python-imaging')
        'PIL'
    
    A global translation where the binary and source translations are different:

        >>> trans.egg_to_source('vanguardistas.builder')
        'python-vanguardistas.builder'
        >>> trans.egg_to_binary('vanguardistas.builder')
        'vanguardistas.builder'

    A locally overridden translation:

        >>> trans.source_to_egg('somesource')
        'someegg'
    
    A debiam package name can only be lowercase, so the default package translation should guess only lowercase names
    (http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Package)

        >>> trans.egg_to_source('EGG')
        'python-egg'
        >>> trans.egg_to_binary('EGG')
        'python-egg'
    """

    def __init__(self, egg_binary_map=None, binary_egg_map=None,
            egg_source_map=None, source_egg_map=None):
        self._egg_binary = egg_binary_map
        if self._egg_binary is None:
            self._egg_binary = {}
        self._egg_source = egg_source_map
        if self._egg_source is None:
            self._egg_source = {}
        self._source_egg = source_egg_map
        if self._source_egg is None:
            self._source_egg = {}
        self._binary_egg = binary_egg_map
        if self._binary_egg is None:
            self._binary_egg = {}

    def _get(self, name, marker, *mappings):
        for m in mappings:
            r = m.get(name, marker)
            if r is not marker:
                return r
        return marker

    def egg_to_binary(self, egg_name):
        """Convert a setuptools name to a debian binary package name."""
        r = self._get(egg_name, _marker, self._egg_binary, _EGG_BINARY_MAP)
        if r is not _marker:
            return r
        return 'python-%s' % egg_name.lower()

    def binary_to_egg(self, binary_name):
        """Convert a debian binary package name to a setuptools name."""
        r = self._get(binary_name, _marker, self._binary_egg, _BINARY_EGG_MAP)
        if r is not _marker:
            return r
        return binary_name[7:] # just get rid of python-

    def source_to_egg(self, source_name):
        """Convert a debian source package name to a setuptools name."""
        r = self._get(source_name, _marker, self._source_egg, _SOURCE_EGG_MAP)
        if r is not _marker:
            return r
        return source_name[7:] # just get rid of python-

    def egg_to_source(self, egg_name):
        """Convert a setuptools name to a debian source package name."""
        r = self._get(egg_name, _marker, self._egg_source, _EGG_SOURCE_MAP)
        if r is not _marker:
            return r
        return 'python-%s' % egg_name.lower()


def version_compare(egg, source):
    if _dpkg_is_gt(egg.version, source.version):
        logging.debug("%s is greater than %s" % (egg.version, source.version))
        return '>'
    logging.debug("%s is NOT greater than %s" % (egg.version, source.version))
    return None # Dunno!!!

def _dpkg_is_gt(v1, v2):
    """
        >>> _dpkg_is_gt('1', '2')
        False
        >>> _dpkg_is_gt('2', '1')
        True
        >>> _dpkg_is_gt('1', '1')
        False
    """
    retcode = call(['dpkg', '--compare-versions', v1, '>>', v2])
    if retcode == 0:
        return True
    return False

# An attempt at a cannonical list of translations
def _read_map(file, map):
    try:
        f = open(file, 'r')
        for line in f.readlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            k, v = line.split()
            assert k not in map, "Duplicate key %s already in map. File %s" % (k, file)
            map[k] = v
    finally:
        f.close()

_EGG_ALL_MAP = {}
_read_map(os.path.join(_here, 'mapping', 'egg_to_all.conf'), _EGG_ALL_MAP)

_EGG_BINARY_MAP = _EGG_ALL_MAP.copy()
_read_map(os.path.join(_here, 'mapping', 'egg_to_bin.conf'), _EGG_BINARY_MAP)

_BINARY_EGG_MAP = dict([(v,k) for (k,v) in _EGG_BINARY_MAP.iteritems()])

_EGG_SOURCE_MAP = _EGG_ALL_MAP.copy()
_read_map(os.path.join(_here, 'mapping', 'egg_to_src.conf'), _EGG_SOURCE_MAP)

_SOURCE_EGG_MAP = dict([(v,k) for (k,v) in _EGG_SOURCE_MAP.iteritems()])
