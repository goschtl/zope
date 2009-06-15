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
import sys
import tempfile
from os.path import exists, join
from subprocess import Popen, PIPE, call
import logging
import optparse
import shutil

from van import pydeb
from setuptools import sandbox
from pkg_resources import to_filename, PathMetadata, Distribution
import apt
import apt_pkg
from zc.lockfile import LockFile

logger = logging.getLogger("van.reposync")

#
# Command Line Interface
#

_COMMANDS = {}

def main(argv=sys.argv):
    # Handle global options and dispatch the command
    assert len(argv) >= 2, "You need to specify a command"
    command = _COMMANDS.get(argv[1])
    if command is None:
        raise Exception("No Command: %s" % argv[1])
    return command(argv)

def _assert_dir(path, context):
    path = os.path.abspath(path)
    assert context.rootdir in path
    if not exists(path):
        logger.debug("Creating %s" % path)
        os.makedirs(path)

def _sync(args=sys.argv):
    command = args[1]
    parser = optparse.OptionParser(usage="usage: %%prog %s argument" % command)
    parser.add_option("--apt-sources", dest="apt_sources", metavar="FILE",
                      help="Load an apt sources.list file into the mirror, "
                           "this only needs to be done once, or whenever you "
                           "want to change the target apt soures.")
    parser.add_option("--root", dest="rootdir",
                      help="The root directory of the mirror.")
    parser.add_option("--loglevel", dest="loglevel", default='INFO',
                      help="The loglevel to output messages at.")
    options, args = parser.parse_args(args)
    assert options.rootdir, "Need to specify root directory for sync"
    assert len(args) == 2, "One and only one command can be specified"
    # setup logging
    loglevel = getattr(logging, options.loglevel)
    logging.basicConfig(level=loglevel)
    # read the apt config we need
    apt_sources = None
    if options.apt_sources:
        apt_sources = open(options.apt_sources, 'r').read()
    context = _ExecutionContext(options.rootdir)
    context.open()
    try:
        pool = join(context.pypi_root, 'download')
        tarballs_to_get = set([])
        owned_files = set([])
        cache, records, depcache = _init_apt_cache(context, apt_sources)
        src = apt_pkg.SourceRecords()
        acq = apt_pkg.Acquire(apt.progress.FetchProgress())
        for package in cache.packages:
            if not package.version_list:
                continue
            src.restart()
            src.lookup(package.name)
            if getattr(src, 'files', None) is None:
                logger.warning("%s has no source package" % package.name)
                continue
            # check for build deps on setuptools
            for build_dep, _, _, _ in src.build_depends:
                if build_dep == 'python-setuptools':
                    break
            else:
                continue
            for md5, size, path, type in src.files:
                destfile = os.path.join(pool, path)
                pool_metadata_filename = '%s.reposync' % destfile
                if exists(pool_metadata_filename):
                    # already got/processed this one, so only mark that we own it
                    owned_files.add(pool_metadata_filename)
                    owned_files.add(destfile)
                    continue
                if type == 'tar':
                    base = os.path.basename(path)
                    dirname = os.path.join(pool, os.path.dirname(path))
                    _assert_dir(dirname, context)
                    apt_pkg.AcquireFile(acq, src.index.archive_uri(path), md5, size, base, destdir=dirname)
                    tarballs_to_get.add((destfile, package.name)) # should only add files we already have or have succeeded in downloading
                else:
                    continue
                owned_files.add(destfile)
        # actually get the tarballs
        acq.run()
        for i in acq.items:
            if i.status != i.stat_done:
                raise Exception("Could not get %s: %s" % (i.destfile, i.error_text))
        # cycle through the tarballs we got and introspect them (also write out links/metadata)
        pypi_simple = join(context.pypi_root, 'simple')
        cant_introspect = set([])
        introspected = set([])
        for pool_file, bin_package_name in tarballs_to_get:
            assert pool in pool_file
            pypi_path = pypi_simple # just put all the tarballs in one directory for now.
            pool_metadata_filename = '%s.reposync' % pool_file
            if exists(pool_metadata_filename):
                continue # we already introspected this file, but for another package name
            owned_files.add(pool_metadata_filename)
            py_data = _get_setuptools_data(pool_file, pydeb.bin_to_py(bin_package_name))
            if py_data is None:
                cant_introspect.add(pool_file)
                continue
            py_project_name, py_version, py_filename = py_data
            pool_metadata_file = open(pool_metadata_filename, 'w')
            pool_metadata_file.write('%s %s %s\n' % py_data)
            pypi_file = os.path.join(pypi_path, py_filename)
            pool_metadata_file.write('%s\n' % pypi_file)
            if exists(pypi_file):
                assert os.path.samefile(pool_file, pypi_file)
                continue
            _assert_dir(pypi_path, context)
            logger.debug("Linking %s to %s" % (pool_file, pypi_file))
            os.symlink(pool_file, pypi_file)
            pool_metadata_file.flush() # we need to read this later, don't want it in buffers
            pool_metadata_file.close()
            introspected.add(pool_file)
            logger.info("Finished introspecting %s" % py_project_name)
        for pool_file in cant_introspect - introspected:
            # write out which files we cannot introspect!
            pool_metadata_filename = '%s.reposync' % pool_file
            pool_metadata_file = open(pool_metadata_filename, 'w')
            pool_metadata_file.write('XXX')
            pool_metadata_file.flush() # we need to read this later, don't want it in buffers
            pool_metadata_file.close()
            logger.info("Marking file unknown, couldn't figure out what this is: %s" % pool_file)
        # writeout our buildout.cfg
        bo_file = []
        for f in owned_files:
            if not f.endswith(".reposync"):
                continue
            pool_metadata = open(f, 'r').read()
            if pool_metadata == 'XXX':
                continue
            py_project_name, py_version, py_filename = pool_metadata.splitlines()[0].split()
            bo_file.append("%s = %s" % (py_project_name, py_version))
        bo_file.sort()
        bo_file.insert(0, '[versions]')
        logger.info("Writing out buildout versions to: %s" % join(context.pypi_root, "buildout_versions.cfg"))
        open(join(context.pypi_root, "buildout_versions.cfg"), 'w').write('\n'.join(bo_file))
        # cleanup
        deferred_remove = set([])
        for path, dirs, files in os.walk(pool):
            if not dirs and not files:
                # cleanup empty dir, XXX need to do this for pypi
                os.rmdir(path)
            for file in files:
                pool_file = os.path.join(path, file)
                if pool_file in owned_files:
                    continue
                # We don't own it, so remove it
                if pool_file.endswith('.reposync'):
                    # remove the metadata in a second stage, we may need it to properly remove links
                    deferred_remove.add(pool_file)
                    continue
                pool_metadata_filename = '%s.reposync' % pool_file
                pool_metadata = None
                if exists(pool_metadata_filename):
                    pool_metadata = open(pool_metadata_filename, 'r').read()
                if pool_metadata is not None and pool_metadata != 'XXX':
                    for f in pool_metadata.splitlines()[1:]:
                        if exists(f):
                            logging.debug("Cleaning/Removing: %s" % f)
                            os.remove(f)
                logging.debug("Cleaning/Removing: %s" % pool_file)
                os.remove(pool_file)
        for f in deferred_remove:
            logging.debug("Cleaning/Removing: %s" % f)
            os.remove(f)
    finally:
        context.close()
    logger.info("Done")
_COMMANDS['sync'] = _sync

#
# Generic Classes
#

def _find(dir, pattern):
    p = Popen(['find', dir, '-name', pattern], stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise Exception('oops')
    return stdout.splitlines()

def _query_setuptools_dist(tarball, tmpdir, py_package_name):
    py_package_filename = to_filename(py_package_name)
    logger.debug("Introspecting egg tarball at %s" % tarball)
    oldcwd = os.getcwd()
    os.chdir(tmpdir)
    try:
        retcode = call(['tar', '-xzf', tarball])
        if retcode != 0:
            logger.error("Failed to unpack egg at %s" % tarball)
            return None
        # find the .egg-info and load it
        found = _find(tmpdir, '%s.egg-info' % py_package_filename)
        if not found:
            logging.warning("Couldn't find %s.egg-info in %s, falling back to looking for *.egg-info" % (py_package_filename, tarball))
            found = _find(tmpdir, '*.egg-info')
        if len(found) != 1:
            logging.error("Found %s egg-info directories, expected 1 (in %s)" % (len(found), tarball))
            return None
        egg_info = found[0]
        basedir = os.path.dirname(egg_info)
        metadata = PathMetadata(basedir, egg_info)
        dist_name = os.path.splitext(os.path.basename(egg_info))[0]
        dist = Distribution(basedir, project_name=dist_name,metadata=metadata)
        return dist
    finally:
        os.chdir(oldcwd)

def _get_setuptools_data(filename, py_package_name):
    """Returns a 3 part tuple:

    (name, version, filename)

    where filename is the setuptools name on the filesystem."""
    tmpdir = tempfile.mkdtemp()
    try:
        try:
            dist = _query_setuptools_dist(filename, tmpdir, py_package_name)
        except:
            logging.exception("Error on introspecting %s, ignoring and continuing anyway." % filename)
            return None
        if dist is None:
            return None
        # I think this is the right way of quoting
        # see: http://mail.python.org/pipermail/distutils-sig/2009-May/011877.html
        return (dist.project_name, dist.version, '%s-%s.tar.gz' % (to_filename(dist.project_name), to_filename(dist.version)))
    finally:
       shutil.rmtree(tmpdir)

class _ExecutionContext(object):
    """Contains the global configuration for what we are doing"""

    _lock = None

    def __init__(self, rootdir):
        self._rootdir = os.path.abspath(rootdir)

    def open(self):
        assert self._lock is None
        self._lock = LockFile(os.path.join(self.rootdir, 'lock'))

    def close(self):
        self._lock.close()
        self._lock = None

    @property
    def rootdir(self):
        return self._rootdir

    @property
    def apt_root(self):
        return os.path.join(self.rootdir, 'apt')

    @property
    def pypi_root(self):
        return os.path.join(self.rootdir, 'pypi')

def _init_apt_cache(context, apt_sources=None):
    join = os.path.join
    exists = os.path.exists
    apt_etc = join(context.apt_root, 'etc', 'apt')
    dpkg_lib = join(context.apt_root, 'var', 'lib', 'dpkg')
    dirs = (apt_etc,
            join(context.apt_root, 'var', 'lib', 'apt', 'lists', 'partial'),
            join(context.apt_root, 'var', 'cache', 'apt', 'archives', 'partial'),
            dpkg_lib)
    # create our directories if they don't already exist
    for d in dirs:
        _assert_dir(d, context)
    # Make the files we need
    dpkg_status = join(dpkg_lib, 'status')
    if not exists(dpkg_status):
        logger.info("Creating %s" % dpkg_status)
        open(dpkg_status, 'w')
    apt_sources_list = join(apt_etc, 'sources.list')
    contents = None
    wanted_contents = apt_sources
    if exists(apt_sources_list):
        contents = open(apt_sources_list, 'r').read()
        if apt_sources is None:
            wanted_contents = contents
    if wanted_contents is None:
        raise Exception("No sources.list setup yet")
    if contents != wanted_contents:
        logger.info("Updating/Creating %s" % apt_sources_list)
        f = open(apt_sources_list, 'w')
        f.write(wanted_contents)
        f.close()
    # get us initialized, but then we don't do much!
    apt_pkg.init()
    config = apt_pkg.config
    apt_pkg.config.set("Dir", context.apt_root)
    apt_pkg.config.set("Dir::State::status", os.path.join(context.apt_root, "var/lib/dpkg/status"))
    cache = apt_pkg.Cache(apt.progress.OpProgress())
    list = apt_pkg.SourceList()
    list.read_main_list()
    lockfile = apt_pkg.config.find_dir("Dir::State::Lists") + "lock"
    lock = apt_pkg.get_lock(lockfile)
    if lock < 0:
        raise Exception("Failed to lock %s" % lockfile)
    try:
        cache.update(apt.progress.FetchProgress(), list)
    finally:
        os.close(lock)
    # re-make the cache with the new lists!
    cache = apt_pkg.Cache(apt.progress.OpProgress())
    depcache = apt_pkg.DepCache(cache)
    records = apt_pkg.PackageRecords(cache)
    return cache, records, depcache
