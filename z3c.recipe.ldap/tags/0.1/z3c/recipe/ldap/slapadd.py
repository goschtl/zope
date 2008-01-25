# -*- coding: utf-8 -*-
"""Recipe slapadd"""

import os, subprocess

class Slapadd(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        options['conf'] = os.path.join(
                buildout['buildout']['directory'], options['conf'])

        if 'slapadd' in options:
            options['slapadd'] = os.path.join(
                buildout['buildout']['directory'], options['slapadd'])
        else:
            options['slapadd'] = 'slapadd'

        self.ldifs = [
            os.path.join(buildout['buildout']['directory'],
                         ldif.strip())
            for ldif in options['ldif'].split('\n') if ldif.strip()]
        options['ldif'] = '\n'.join(self.ldifs)

    def install(self):
        """installer"""
        args = [self.options['slapadd'], '-f', self.options['conf']]
        for ldif in self.ldifs:
            subprocess.Popen(args+['-l', ldif]).wait()
        return ()

    def update(self):
        """updater"""
        return self.install()

