##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

import logging, os, shutil
import zc.recipe.egg
import zc.buildout
import ZConfig.cfgparser
import cStringIO

logger = logging.getLogger('zc.zodbrecipes')

class StorageServer:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        deployment = self.deployment = options.get('deployment')
        if deployment:
            options['rc-directory'] = buildout[deployment]['rc-directory']
            options['run-directory'] = buildout[deployment]['run-directory']
            options['log-directory'] = buildout[deployment]['log-directory']
            options['etc-directory'] = buildout[deployment]['etc-directory']
            options['logrotate'] = os.path.join(
                buildout[deployment]['logrotate-directory'],
                deployment + '-' + name)
            options['crontab-directory'] = buildout[
                deployment]['crontab-directory']
            options['user'] = buildout[deployment]['user']
        else:
            options['rc-directory'] = buildout['buildout']['bin-directory']
            options['run-directory'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
                )

        options['scripts'] = ''
        options['eggs'] = options.get('eggs', 'zdaemon\nsetuptools')
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

        options['runzeo'] = os.path.join(
            buildout['buildout']['bin-directory'],
            options.get('runzeo', 'runzeo'),
            )
        options['zeopack'] = os.path.join(
            buildout['buildout']['bin-directory'],
            options.get('zeopack', 'zeopack'),
            )

    def install(self):
        options = self.options

        if not os.path.exists(options['runzeo']):
            logger.warn(no_runzeo % options['runzeo'])

        run_directory = options['run-directory']
        deployment = self.deployment
        if deployment:
            zeo_conf_path = os.path.join(options['etc-directory'],
                                         self.name+'-zeo.conf')
            zdaemon_conf_path = os.path.join(options['etc-directory'],
                                             self.name+'-zdaemon.conf')
            event_log_path = os.path.join(options['log-directory'],
                                          self.name+'-zeo.log')
            socket_path = os.path.join(run_directory,
                                       self.name+'-zdaemon.sock')
            rc = deployment + '-' + self.name

            logrotate = options['logrotate']
            open(logrotate, 'w').write(logrotate_template % dict(
                logfile=event_log_path,
                rc=rc,
                ))
            
            creating = [zeo_conf_path, zdaemon_conf_path, logrotate,
                        os.path.join(options['rc-directory'], rc),
                        ]

            pack = options.get('pack')
            if pack:
                pack = pack.split()
                if len(pack) < 5:
                    raise zc.buildout.UserError(
                        'Too few crontab fields in pack specification')
                if len(pack) > 6:
                    raise zc.buildout.UserError(
                        'Too many values in pack option')
                pack_path = os.path.join(
                    options['crontab-directory'],
                    "pack-%s-%s" % (deployment, self.name),
                    )
                if not os.path.exists(options['zeopack']):
                    logger.warn("Couln'e find zeopack script, %r",
                                options['zeopack'])
        else:
            zeo_conf_path = os.path.join(run_directory, 'zeo.conf')
            zdaemon_conf_path = os.path.join(run_directory, 'zdaemon.conf')
            event_log_path = os.path.join(run_directory, 'zeo.log')
            socket_path = os.path.join(run_directory, 'zdaemon.sock')
            rc = self.name
            creating = [run_directory,
                        os.path.join(options['rc-directory'], rc),
                        ]
            if not os.path.exists(run_directory):
                os.mkdir(run_directory)
            pack = pack_path = None

        try:
            zeo_conf = options.get('zeo.conf', '')+'\n'
            zeo_conf = ZConfigParse(cStringIO.StringIO(zeo_conf))

            zeo_section = [s for s in zeo_conf.sections if s.type == 'zeo']
            if not zeo_section:
                raise zc.buildout.UserError('No zeo section was defined.')
            if len(zeo_section) > 1:
                raise zc.buildout.UserError('Too many zeo sections.')
            zeo_section = zeo_section[0]
            if not 'address' in zeo_section:
                raise zc.buildout.UserError('No ZEO address was specified.')

            storages = [s.name for s in zeo_conf.sections
                        if s.type not in ('zeo', 'eventlog', 'runner')
                        ]

            if not storages:
                raise zc.buildout.UserError('No storages were defined.')

            if not [s for s in zeo_conf.sections if s.type == 'eventlog']:
                zeo_conf.sections.append(event_log('STDOUT'))

            zdaemon_conf = options.get('zdaemon.conf', '')+'\n'
            zdaemon_conf = ZConfigParse(cStringIO.StringIO(zdaemon_conf))

            defaults = {
                'program': "%s -C %s" % (options['runzeo'], zeo_conf_path),
                'daemon': 'on',
                'transcript': event_log_path,
                'socket-name': socket_path,
                'directory' : run_directory,
                }
            if deployment:
                defaults['user'] = options['user']
            runner = [s for s in zdaemon_conf.sections
                      if s.type == 'runner']
            if runner:
                runner = runner[0]
            else:
                runner = ZConfigSection('runner')
                zdaemon_conf.sections.insert(0, runner)
            for name, value in defaults.items():
                if name not in runner:
                    runner[name] = value

            if not [s for s in zdaemon_conf.sections
                    if s.type == 'eventlog']:
                zdaemon_conf.sections.append(event_log(event_log_path))

            zdaemon_conf = str(zdaemon_conf)

            self.egg.install()
            requirements, ws = self.egg.working_set()

            open(zeo_conf_path, 'w').write(str(zeo_conf))
            open(zdaemon_conf_path, 'w').write(str(zdaemon_conf))

            self.egg.install()
            requirements, ws = self.egg.working_set()

            zc.buildout.easy_install.scripts(
                [(rc, 'zdaemon.zdctl', 'main')],
                ws, options['executable'], options['rc-directory'],
                arguments = ('['
                             '\n        %r, %r,'
                             '\n        ]+sys.argv[1:]'
                             '\n        '
                             % ('-C', zdaemon_conf_path,
                                )
                             ),
                )

            if pack:
                address = zeo_section['address']
                if ':' in address:
                    host, port = address.split(':')
                    address = '-h %s -p %s' % (host, port)
                else:
                    try:
                        port = int(address)
                    except:
                        address = '-U '+address
                    else:
                        address = '-p '+address
                f = open(pack_path, 'w')
                if len(pack) == 6:
                    days = pack[5]
                    pack = pack[:5]
                else:
                    days = 1
                for storage in storages:
                    f.write("%s %s %s -S %s -d %s\n" % (
                            ' '.join(pack),
                            options['zeopack'],
                            address, storage, days))
                f.close()

            return creating

        except:
            for f in creating:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.exists(f):
                    os.remove(f)
            raise


    update = install

no_runzeo = """
A runzeo script couldn't be found at:

  %r

You may need to generate a runzeo script using the
zc.recipe.eggs:script recipe and the ZODB3 egg, or you may need
to specify the location of a script using the runzeo option.
"""


def event_log(path, *data):
    return ZConfigSection(
        'eventlog', '', None,
        [ZConfigSection('logfile', '',
                        dict(path=path)
                        )
         ],
        )

event_log_template = """
<eventlog>
  <logfile>
    path %s
    formatter zope.exceptions.log.Formatter
  </logfile>
</eventlog>
"""

logrotate_template = """%(logfile)s {
  rotate 5
  weekly
  postrotate
    %(rc)s reopen_transcript
  endscript
}
"""


class ZConfigResource:

    def __init__(self, file, url=''):
        self.file, self.url = file, url

class ZConfigSection(dict):

    imports = ()

    def __init__(self, type='', name='', data=None, sections=None):
        dict.__init__(self)
        if data:
            self.update(data)
        self.sections = sections or []
        self.type, self.name = type, name

    def addValue(self, key, value, *args):
        self[key] = value

    def __str__(self, pre=''):
        result = []
        if self.type:
            if self.name:
                result = ['%s<%s %s>' % (pre, self.type, self.name)]
            else:
                result = ['%s<%s>' % (pre, self.type)]
            pre += '  '

        if self.imports:
            for pkgname in self.imports:
                result.append('%import '+pkgname)
            result.append('')

        for name, value in sorted(self.items()):
            result.append('%s%s %s' % (pre, name, value))

        if self.sections and self:
            result.append('')

        for section in self.sections:
            result.append(section.__str__(pre))
        
        if self.type:
            result.append('%s</%s>' % (pre[:-2], self.type))
            result.append('')
                          
        return '\n'.join(result).rstrip()+'\n'
  
class ZConfigContext:

    def __init__(self):
        self.top = ZConfigSection()
        self.sections = []

    def startSection(self, container, type, name):
        newsec = ZConfigSection(type, name)
        container.sections.append(newsec)
        return newsec

    def endSection(self, container, type, name, newsect):
        pass

    def importSchemaComponent(self, pkgname):
        self.top.imports += (pkgname, )

    def includeConfiguration(self, section, newurl, defines):
        raise NotImplementedError('includes are not supported')

def ZConfigParse(file):
    c = ZConfigContext()
    ZConfig.cfgparser.ZConfigParser(ZConfigResource(file), c).parse(c.top)
    return c.top
