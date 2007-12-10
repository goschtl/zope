# -*- coding: utf-8 -*-
"""Recipe ldap"""

import sys, os, signal, subprocess

import zc.buildout
import zc.recipe.egg

import conf

class Slapd(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.name, self.options = name, options

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], name)

        if 'slapd' in options:
            options['slapd'] = os.path.join(
                buildout['buildout']['directory'], options['slapd'])
        else:
            options['slapd'] = 'slapd'

        if 'conf' not in options:
            options['conf'] = os.path.join(
                options['location'], name+'.conf')

        if 'pidfile' not in options:
            options['pidfile'] = os.path.join(
                options['location'], name+'.pid')

        if 'directory' not in options:
            options['directory'] = os.path.join(
                buildout['buildout']['directory'], 'var', name)

        if 'urls' in options and 'use-socket' in options:
            raise ValueError('Cannot specify both the "urls" and '
                             '"use-socket" options') 
        if 'use-socket' in options:
            options['urls'] = 'ldapi://%s' % os.path.join(
                options['location'], name+'.socket').replace(
                '/', '%2F')

        # Initialize the conf options
        conf.init_options(
            options, dir=buildout['buildout']['directory'])

    def install(self):
        """installer"""
        # Install slapd.conf
        os.makedirs(self.options['location'])
        conf_file = file(self.options['conf'], 'w')
        conf_file.writelines(conf.get_lines(self.options))
        conf_file.close()

        if not os.path.exists(self.options['directory']):
            # Install the DB dir
            os.makedirs(self.options['directory'])

        # Install the control script
        _, ws = self.egg.working_set(['z3c.recipe.ldap'])
        zc.buildout.easy_install.scripts(
            [(self.name, 'z3c.recipe.ldap.ctl', 'main')],
            ws, self.options['executable'],
            self.options['bin-directory'],
            arguments=repr(self.options))

        return (self.options['location'],)

    def update(self):
        """updater"""
        pass
