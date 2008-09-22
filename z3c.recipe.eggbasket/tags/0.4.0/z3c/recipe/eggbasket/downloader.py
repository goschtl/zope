# -*- coding: utf-8 -*-
"""Recipe eggbasket"""

import logging
import tempfile
import shutil
import os
import tarfile
import urllib
from zc.recipe.egg import Eggs
from z3c.recipe.eggbasket.utils import distributions_are_installed_in_dir
from z3c.recipe.eggbasket.utils import install_distributions


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
            log.info("Distributions are not installed. "
                     "A tarball will be downloaded.")
            tarball_name = url.split('/')[-1]
            log.info("Downloading %s ..." % url)

            try:
                # Make temporary files and directories.
                extraction_dir = tempfile.mkdtemp()
                filenum, temp_tarball_name = tempfile.mkstemp()

                tarball = open(temp_tarball_name, 'w')
                try:
                    tarball.write(urllib.urlopen(url).read())
                except IOError:
                    log.error("Url not found: %s." % url)
                    return tuple()
                tarball.close()
                log.info("Finished downloading.")
                log.info("Extracting tarball contents...")

                try:
                    tf = tarfile.open(temp_tarball_name, 'r:gz')
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
                shutil.rmtree(extraction_dir)
                os.unlink(temp_tarball_name)

        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        return tuple()

    def update(self):
        # This recipe only needs to be called once.
        pass
