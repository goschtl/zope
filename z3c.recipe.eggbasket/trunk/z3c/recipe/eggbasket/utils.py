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


def create_source_tarball():
    # These variables need to be configurable:
    egg = 'grok'
    version = '0.13'
    config_file_name = 'buildout.cfg'
    links = ['http://download.zope.org/distribution/']

    import zc.buildout.easy_install
    import zc.buildout.buildout
    import os

    # Read the buildout file.
    here = os.getcwd()
    config_file = os.path.join(here, config_file_name)
    config = zc.buildout.buildout._open(here, config_file, [])

    # Get the version information.
    versions = config['buildout'].get('versions')
    if version is not None:
        versions = config[versions]

    try:
        # Make temporary directories for the cache and the destination
        # eggs directory.  The cache is the important one here as that is
        # where the sources get downloaded to.
        cache = tempfile.mkdtemp()
        dest = tempfile.mkdtemp()
        # Set the download cache directory:
        zc.buildout.easy_install.download_cache(cache)

        # Install the main egg, which pulls all dependencies into the
        # download cache.
        ws = zc.buildout.easy_install.install(
            [egg], dest, versions=versions,
            links=links)

        # Create tarball in current directory.
        directory_name = '%s-eggs-%s' % (egg, version)
        egg_tar = tarfile.open(directory_name + '.tgz', 'w:gz')
        egg_tar.add(cache, directory_name)
        # TODO: actually add latest version of grok egg
        egg_tar.close()
    finally:
        shutil.rmtree(dest)
        shutil.rmtree(cache)
