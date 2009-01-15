# -*- coding: utf-8 -*-
"""Recipe eggbasket"""

import logging
import tempfile
import shutil
import os
import tarfile
from zc.recipe.egg import Eggs
from z3c.recipe.eggbasket.utils import distributions_are_installed_in_dir
from z3c.recipe.eggbasket.utils import install_distributions
from z3c.recipe.eggbasket.utils import download_tarball


class Downloader(Eggs):
    """zc.buildout recipe for getting eggs out of a tar ball"""

    def install(self):
        """Installer
        """
        log = logging.getLogger(self.name)
        if self.buildout['buildout'].get('offline') == 'true':
            log.error("Cannot run in offline mode.")
            return tuple()
        options = self.options

        distributions = [
            r.strip()
            for r in options.get('eggs', self.name).split('\n')
            if r.strip()]

        url = self.options.get('url')

        if not distributions_are_installed_in_dir(distributions,
                                                  options['eggs-directory']):
            log.info("Not all distributions are installed. "
                     "A tarball will be downloaded.")
            tarball_name = url.split('/')[-1]

            # If the user has specified a download directory (in
            # ~/.buildout/default.cfg probably) we will want to use
            # it.
            download_dir = self.buildout['buildout'].get('download-directory')
            if download_dir:
                if not os.path.exists(download_dir):
                    os.mkdir(download_dir)
                if not os.path.isdir(download_dir):
                    # It exists but is not a file: we are not going to
                    # use the download dir.
                    download_dir = None

            keep_tarball = False
            if download_dir:
                keep_tarball = True
                tarball_location = os.path.join(download_dir, tarball_name)
                if os.path.exists(tarball_location):
                    log.info("Using already downloaded %s" % tarball_location)
                else:
                    result = download_tarball(tarball_location, url)
                    if not result:
                        # Give up.
                        return tuple()

            if not keep_tarball:
                # Make temporary file.
                try:
                    filenum, tarball_location = tempfile.mkstemp()
                except:
                    log.error("Could not create temporary tarball file")
                    # Reraise exception
                    raise
                result = download_tarball(tarball_location, url)
                if not result:
                    return tuple()

            # We have the tarball.  Now we make a temporary extraction
            # directory.
            try:
                extraction_dir = tempfile.mkdtemp()
            except:
                log.error("Could not create temporary extraction directory")
                # Reraise exception
                raise

            try:
                log.info("Extracting tarball contents...")
                try:
                    tf = tarfile.open(tarball_location, 'r:gz')
                except tarfile.ReadError, e:
                    # Likely the download location is wrong and gives a 404.
                    # Or the tarball is not zipped.
                    log.error("No correct tarball found at %s." % url)
                    log.error("The error was: %s" % e)
                    return tuple()

                links = []
                for name in tf.getnames():
                    tf.extract(name, extraction_dir)
                    links.append(os.path.join(extraction_dir, name))
                tf.close()

                log.info("Installing eggs to %s which will take a while..."
                         % options['eggs-directory'])
                result = install_distributions(
                    distributions, options['eggs-directory'],
                    links = links)
                if result is False:
                    log.error("Failed to install required eggs with the tar "
                              "ball.")
            finally:
                if not keep_tarball:
                    os.unlink(tarball_location)
                shutil.rmtree(extraction_dir)

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        # This recipe only needs to be called once.
        pass
