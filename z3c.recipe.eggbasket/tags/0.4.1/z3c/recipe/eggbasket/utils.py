import logging
import os.path
import re
import shutil
import sys
import tarfile
import tempfile
import urllib

# XXX We may want to add command line argument handling.
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-5s %(name)-12s %(message)s')


def install_distributions(distributions, target_dir, links=[],
                          use_empty_index=False):
    """Install distributions.

    Distributions is a list of requirements, e.g. ['grok==0.13']

    When use_empty_index is True we only try to install the required
    distributions by using the supplied links.  We do not use the
    python cheese shop index then.

    """
    from zc.buildout.easy_install import install
    from zc.buildout.easy_install import MissingDistribution
    log = logging.getLogger('eggbasket.utils')

    if use_empty_index:
        # When the temp dir is not writable this throws an OSError,
        # which we might want to catch, but actually it is probably
        # fine to just let it bubble up to the user.
        try:
            empty_index = tempfile.mkdtemp()
        except:
            log.error("Could not create temporary file")
            # Reraise exception
            raise
        index = 'file://' + empty_index
    else:
        # Use the default index (python cheese shop)
        index = None
    try:
        try:
            install(distributions, target_dir, newest=False,
                    links=links, index=index)
        except MissingDistribution:
            return False
        else:
            return True
    finally:
        if use_empty_index:
            shutil.rmtree(empty_index)


def distributions_are_installed_in_dir(distributions, target_dir):
    # Check if the required distributions are installed.  We do this
    # by trying to install the distributions in the target dir and
    # letting easy_install only look inside that same target dir while
    # doing that.
    result = install_distributions(distributions, target_dir,
                                   links=[target_dir], use_empty_index=True)
    return result


def create_source_tarball(egg=None, versionfile='buildout.cfg'):
    log = logging.getLogger('eggbasket.utils')
    if egg is None:
        # XXX Having a way to read the setup.py in the current
        # directory and get an egg name and perhaps version number
        # from there would be cool.  For now:
        log.error("Please provide an egg name.")
        sys.exit(1)

    # XXX This may be a bit too hard coded.
    # Perhaps try to read something from the buildout config.
    links = ['http://download.zope.org/distribution/']

    import zc.buildout.easy_install
    import zc.buildout.buildout

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
        log.error("Could not get versions from %s.", versionfile)
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
            log.error("The main egg (%s) has not been pinned in the "
                      "version file (%s)." % (egg, versionfile))
            sys.exit(1)

        # Install the main egg, which pulls all dependencies into the
        # download cache.
        log.info("Will get main egg (%s) version %s and dependencies "
                 "with versions as listed in %s." %
                 (egg, main_egg_version, versionfile))
        log.info("This could take a while...")
        ws = zc.buildout.easy_install.install(
            [egg], dest, versions=versions,
            links=links)

        # TODO: Make this optional:
        log.info("Getting extra Windows distributions...")
        egg_expression = re.compile(r'(.*)-([^-]*)(\.tar.gz|-py-*\.egg)')
        for package in os.listdir(cache):
            results = egg_expression.findall(package)
            if len(results) != 1:
                continue
            parts = results[0]
            if len(parts) != 3:
                continue
            package, version, dummy = parts
            get_windows_egg(package, version, cache)

        # Create tarball in current directory.
        directory_name = '%s-eggs-%s' % (egg, main_egg_version)
        tar_name = directory_name + '.tgz'
        log.info("Creating %s", tar_name)
        egg_tar = tarfile.open(tar_name, 'w:gz')
        egg_tar.add(cache, directory_name)

        # TODO: perhaps actually add latest version of grok egg if it
        # is not there already, though currently the code should have
        # failed already when this it is not available.
        egg_tar.close()
        log.info("Done.")
    finally:
        shutil.rmtree(dest)
        shutil.rmtree(cache)


def get_windows_egg(package, version, target_dir):
    log = logging.getLogger('eggbasket.utils')
    base_url = 'http://pypi.python.org/simple/'
    package_page = base_url + package
    try:
        contents = urllib.urlopen(package_page).read()
    except IOError:
        log.warn("%s not found.", package_page)
        return

    # We expect to get html with lines like this:
    #
    # <a href='http://pypi.python.org/packages/source/m/martian/martian-0.9.6.tar.gz#md5=98cda711bda0c5f45a05e2bdc2dc0d23'>martian-0.9.6.tar.gz</a><br/>
    #
    # We want to look for http....package-version-py2.x-win32.egg
    expression = r'[\'"]http.*/%s-%s-py.*win32.egg.*[\'"]' % (package, version)
    findings = re.compile(expression).findall(contents)
    log.debug("Found %s matches.", len(findings))
    for finding in findings:
        # Strip off the enclosing single or double quotes:
        finding = finding[1:-1]
        # We probably have something like:
        # ...egg#md5=3fa5e992271375eac597622d8e2fd5ec'
        parts = finding.split('#md5=')
        url = parts[0]
        if len(parts) == 2:
            md5hash = parts[1]
        else:
            md5hash = ''

        target = os.path.join(target_dir, url.split('/')[-1])
        log.info("Downloading %s to %s", url, target)
        try:
            urllib.urlretrieve(url, target)
        except IOError:
            log.error("Download error.")
        else:
            log.info("Finished downloading.")
            # TODO: check md5hash
