##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Create a system deployment for an application

$Id: deployment.py 14934 2006-11-10 23:57:33Z jim $
"""

import grp, logging, os, pwd, shutil
import zc.buildout

logger = logging.getLogger('zc.recipe.deployment')

class Install:

    def __init__(self, buildout, name, options):
        self.options = options
        if not options.get('name'):
            options['name'] = name

        name = options['name']

        create = []
        options['prefix'] = options.get('prefix', '/')
        options['run-directory'] = os.path.join(
            options['prefix'], options.get('run', 'var/run'), name)
        options['log-directory'] = os.path.join(
            options['prefix'], options.get('log', 'var/log'), name)
        options['etc-directory'] = os.path.join(
            options['prefix'], options.get('etc', 'etc'), name)
        etc = os.path.join(options['prefix'], options.get('etc', 'etc'))
        options['crontab-directory'] = options.get(
            'crontab-directory', os.path.join(etc, 'cron.d'))
        options['rc-directory'] = options.get(
            'rc-directory', os.path.join(etc, 'init.d'))
        options['logrotate-directory'] = options.get(
            'logrotate-directory', os.path.join(etc, 'logrotate.d'))

    def install(self):
        options = self.options
        run_user = options['user']
        etc_user = options.get('etc-user', 'root')
        run_uid, run_gid = pwd.getpwnam(run_user)[2:4]
        etc_uid, etc_gid = pwd.getpwnam(etc_user)[2:4]
        created = []
        try:
            make_dir(options['etc-directory'], etc_uid, etc_gid, 0755, created)
            make_dir(options['log-directory'], run_uid, run_gid, 0755, created)
            make_dir(options['run-directory'], run_uid, run_gid, 0750, created)
            if options['prefix'] != '/':
                make_dir(options['crontab-directory'],
                         etc_uid, etc_gid, 0755, created)
                make_dir(options['rc-directory'],
                         etc_uid, etc_gid, 0755, created)
                make_dir(options['logrotate-directory'],
                         etc_uid, etc_gid, 0755, created)
        except Exception:
            for d in created:
                try:
                    shutil.rmtree(d)
                except OSError:
                    # parent directory may have already been removed
                    pass
            raise

        return ()

    def update(self):
        pass


def uninstall(name, options):
    path = options['etc-directory']
    if os.path.isdir(path):
        shutil.rmtree(path)
        logger.info("Removing %r", path)
    directories = ()
    if options.get('prefix', '/') != '/':
        directories = ('crontab', 'rc', 'logrotate')
    for d in directories + ('log', 'run'):
        path = options[d+'-directory']
        if os.path.isdir(path):
            if os.listdir(path):
                logger.warn("Can't remove non-empty directory %r.", path)
            else:
                os.rmdir(path)
                logger.info("Removing %r.", path)

def make_dir(name, uid, gid, mode, created):
    uname = pwd.getpwuid(uid)[0]
    gname = grp.getgrgid(gid)[0]
    if not os.path.isdir(name):
        os.makedirs(name, mode)
        created.append(name)
        logger.info('\n    Creating %r,\n    mode %o, user %r, group %r',
                    name, mode, uname, gname)
    else:
        os.chmod(name, mode)
        logger.info('\n    Updating %r,\n    mode %o, user %r, group %r',
                    name, mode, uname, gname)

    os.chown(name, uid, gid)

class Configuration:

    def __init__(self, buildout, name, options):
        self.options = options

        deployment = options.get('deployment')
        if deployment:
            options['location'] = os.path.join(
                buildout[deployment]['etc-directory'],
                name)
        else:
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                name)

    def install(self):
        options = self.options
        mode = options.get('mode', '')
        if 'file' in options:
            if 'text' in options:
                raise zc.buildout.UserError(
                    "Cannot specify both file and text options")
            text = open(options['file'], 'r'+mode).read()
        else:
            text = options['text']
        open(options['location'], 'w'+mode).write(text)
        return options['location']

    update = install

class Crontab:

    def __init__(self, buildout, name, options):
        self.options = options

        deployment = options['deployment']
        user = options.get('user', buildout[deployment]['user'])
        deployment_name = buildout[deployment]['name']
        options['location'] = os.path.join(
            buildout[deployment]['crontab-directory'],
            deployment_name + '-' + name)
        options['entry'] = '%s\t%s\t%s\n' % (
            options['times'], user, options['command'])

    def install(self):
        options = self.options
        open(options['location'], 'w').write(options['entry'])
        return options['location']

    update = install

