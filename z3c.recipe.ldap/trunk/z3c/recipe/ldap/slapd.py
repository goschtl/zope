# -*- coding: utf-8 -*-
"""Recipe ldap"""

import sys, os, signal, subprocess

import zc.buildout
import zc.recipe.egg

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
            options['urls'] = 'ldapi:/%s' % os.path.join(
                options['location'], name+'.socket')

        # Initialize the conf options
        init_conf_options(
            options, dir=buildout['buildout']['directory'])

    def install(self):
        """installer"""
        # Install slapd.conf
        os.makedirs(self.options['location'])
        conf = file(self.options['conf'], 'w')
        conf.writelines(get_conf_lines(self.options))
        conf.close()

        if not os.path.exists(self.options['directory']):
            # Install the DB dir
            os.makedirs(self.options['directory'])

        # Install the control script
        _, ws = self.egg.working_set(['z3c.recipe.ldap'])
        zc.buildout.easy_install.scripts(
            [(self.name, 'z3c.recipe.ldap.slapd', 'ctl')],
            ws, self.options['executable'],
            self.options['bin-directory'],
            arguments=repr(self.options))

        return (self.options['location'],)

    def update(self):
        """updater"""
        pass

conf_exclude = [
    'slapd', 'conf', 'urls', 'recipe', 'location', 'executable',
    'bin-directory', 'eggs-directory', 'develop-eggs-directory',
    '_e', '_d', '_b']
conf_paths = [
    'include', 'pidfile', 'argsfile', 'directory', 'modulepath']
conf_multiple = ['include', 'moduleload', 'access', 'index']
conf_defaults = [('modulepath', '/usr/lib/ldap'),
                 ('moduleload', 'back_bdb'),
                 ('database', 'bdb'),
                 ('index', 'objectClass\teq')]
conf_order = [
    'include', 'pidfile', 'argsfile', 'access', 'modulepath',
    'moduleload', 'database', 'suffix', 'directory', 'index']

def init_conf_options(options, dir='.', exclude=conf_exclude,
                      paths=conf_paths, multiple=conf_multiple,
                      defaults=conf_defaults):
    for key, value in defaults:
        if key not in options:
            options[key] = value

    for key, value in options.iteritems():
        if key in exclude:
            continue

        if key in multiple:
            values = []
            for v in value.split('\n'):
                v = v.strip()
                if not v:
                    continue
                if key in paths:
                    # expand file paths
                    v = os.path.join(dir, v)
                values.append(v)
            options[key] = '\n'.join(values)
            continue

        if key in paths:
            options[key] = os.path.join(dir, value)

def order_keys(keys, order=conf_order):
    for key in order:
        if key in keys:
            yield key
    for key in keys:
        if key not in order:
            yield key

def get_conf_lines(options, exclude=conf_exclude,
                   multiple=conf_multiple, template='%s\t%s\n'):
    for key in order_keys(options):
        if key in exclude:
            continue

        value = options[key]
        if key in multiple:
            for v in value.split('\n'):
                yield template % (key, v)
        else:
            yield template % (key, value)

def ctl(options):
    command, = sys.argv[1:]
    if command.lower() == 'start':
        args = [options['slapd'], '-f', options['conf']]
        if 'urls' in options:
            args.extend(['-h', options['urls']])
        subprocess.Popen(args)
    elif command.lower() == 'stop':
        pidfile = file(options['pidfile'])
        pid = int(pidfile.read())
        pidfile.close()
        os.kill(pid, signal.SIGTERM)
    else:
        raise ValueError('Command %s unsupported' % command)
