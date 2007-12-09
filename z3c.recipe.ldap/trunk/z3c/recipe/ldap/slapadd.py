# -*- coding: utf-8 -*-
"""Recipe slapadd"""

import os

class Slapadd(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        self.ldifs = [
            os.path.join(buildout['buildout']['directory'],
                         ldif.strip())
            for ldif in options['ldif'].split('\n') if ldif.strip()]
        options['ldif'] = '\n'.join(self.ldifs)

        var = options.get('var')
        if var is None:
            self.var = options['var'] = os.path.join(
                buildout['buildout']['directory'],
                'var', self.name)
        else:
            self.var = options['var'] = os.path.join(
                buildout['buildout']['directory'], var)

    def install(self):
        """installer"""
        if not os.path.exists(self.var):
            os.mkdir(self.var)
        
        return tuple()

    def update(self):
        """updater"""
        pass

