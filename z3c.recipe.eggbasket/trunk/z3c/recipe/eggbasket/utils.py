import sys
import tempfile
import shutil
import tarfile


def install_distributions(distributions, target_dir, links=[]):
    from zc.buildout.easy_install import install
    from zc.buildout.easy_install import MissingDistribution
    try:
        empty_index = tempfile.mkdtemp()

        try:
            install(distributions, target_dir, newest=False,
                    links=links, index='file://' + empty_index)
        except MissingDistribution:
            return False
        else:
            return True
    finally:
        shutil.rmtree(empty_index)


def distributions_are_installed_in_dir(distributions, target_dir):
    # Check if the required distributions are installed.  We do this
    # by trying to install the distributions in the target dir and
    # letting easy_install only look inside that same target dir while
    # doing that.
    result = install_distributions(distributions, target_dir,
                                   links=[target_dir])
    return result


def create_source_tarball(egg=None, versionfile='buildout.cfg'):
    # XXX We may want to add command line argument handling.

    if egg is None:
        # XXX Having a way to read the setup.py in the current
        # directory and get an egg name and perhaps version number
        # from there would be cool.  For now:
        print "Please provide an egg name."
        sys.exit(1)

    # XXX This may be a bit too hard coded.
    # Perhaps try to read something from the buildout config.
    links = ['http://download.zope.org/distribution/']

    import zc.buildout.easy_install
    import zc.buildout.buildout
    import os

    # Read the buildout/versions file.  versionfile can be a file in
    # the current working directory or on some url.  zc.buildout
    # nicely takes care of that for us.
    config = zc.buildout.buildout._open(os.getcwd(), versionfile, [])

    # Get the version information.
    buildout = config.get('buildout')
    if buildout is None:
        versions = config.get('versions')
    else:
        versions = buildout.get('versions')
        if versions is not None:
            versions = config.get(versions)
    if versions is None:
        print "Could not get versions from %s." % versionfile
        sys.exit(1)

    try:
        # Make temporary directories for the cache and the destination
        # eggs directory.  The cache is the important one here as that is
        # where the sources get downloaded to.
        cache = tempfile.mkdtemp()
        dest = tempfile.mkdtemp()
        # Set the download cache directory:
        zc.buildout.easy_install.download_cache(cache)

        main_egg_version = versions.get(egg)
        if main_egg_version is None:
            print ("Error: the main egg (%s) has not been pinned in the "
                   "version file (%s)." % (egg, versionfile))
            sys.exit(1)

        # Install the main egg, which pulls all dependencies into the
        # download cache.
        print ("Will get main egg (%s) version %s and dependencies "
               "with versions as listed in %s." %
               (egg, main_egg_version, versionfile))
        print "This could take a while..."
        ws = zc.buildout.easy_install.install(
            [egg], dest, versions=versions,
            links=links)

        # Create tarball in current directory.
        directory_name = '%s-eggs-%s' % (egg, main_egg_version)
        tar_name = directory_name + '.tgz'
        print "Creating", tar_name
        egg_tar = tarfile.open(tar_name, 'w:gz')
        egg_tar.add(cache, directory_name)

        # TODO: perhaps actually add latest version of grok egg if it
        # is not there already, though currently the code should have
        # failed already when this it is not available.
        egg_tar.close()
        print "Done."
    finally:
        shutil.rmtree(dest)
        shutil.rmtree(cache)
