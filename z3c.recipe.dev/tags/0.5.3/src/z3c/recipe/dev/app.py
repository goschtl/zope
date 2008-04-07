##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Z3c development recipes

$Id:$
"""

import os, sys, shutil
import zc.buildout
import zc.recipe.egg
import pkg_resources
import ZConfig.schemaless
import cStringIO

server_types = {
    # name     (module,                  http-name)
    'twisted': ('zope.app.twisted.main', 'HTTP'),
    'zserver': ('zope.app.server.main',  'WSGI-HTTP'),
    }

class AppSetup:

    def __init__(self, buildout, name, options):
        self.egg = None
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        if not options.get('working-directory', ''):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'], name)

        if options.get('eggs'):
            self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options
        location = options['location']
        executable = self.buildout['buildout']['executable']

        # setup path
        dest = []
        if not os.path.exists(location):
            os.mkdir(location)
            dest.append(location)

        event_log_path = os.path.join(location, 'z3.log')
        access_log_path = os.path.join(location, 'access.log')
        site_zcml_path = os.path.join(location, 'site.zcml')
        principals_zcml_path = os.path.join(location, 'principals.zcml')
        securitypolicy_zcml_path = os.path.join(location, 'securitypolicy.zcml')

        # append files to dest whihc should get removed on update
        dest.append(site_zcml_path)
        dest.append(principals_zcml_path)
        dest.append(securitypolicy_zcml_path)


        # setup site.zcml
        open(site_zcml_path, 'w').write(
            site_zcml_template % self.options['site.zcml']
            )

        # setup principals.zcml
        open(principals_zcml_path, 'w').write(
            principals_zcml_template % self.options['principals.zcml']
            )

        # setup securitypolicy.zcml
        open(securitypolicy_zcml_path, 'w').write(
            securitypolicy_zcml_template % self.options['securitypolicy.zcml']
            )

        # setup zope.conf
        zope_conf = options.get('zope.conf', '')+'\n'
        zope_conf = ZConfig.schemaless.loadConfigFile(
            cStringIO.StringIO(zope_conf))

        zope_conf['site-definition'] = [site_zcml_path]

        server_type = server_types[options['server']][1]
        for address in options.get('address', '').split():
            zope_conf.sections.append(
                ZConfig.schemaless.Section(
                    'server',
                    data=dict(type=[server_type], address=[address]))
                )
        if not [s for s in zope_conf.sections
                if ('server' in s.type)]:
            zope_conf.sections.append(
                ZConfig.schemaless.Section(
                    'server',
                    data=dict(type=[server_type], address=['8080']))
                )

        if not [s for s in zope_conf.sections if s.type == 'zodb']:
            raise zc.buildout.UserError(
                'No database sections have been defined.')

        if not [s for s in zope_conf.sections if s.type == 'accesslog']:
            zope_conf.sections.append(access_log(access_log_path))

        if not [s for s in zope_conf.sections if s.type == 'eventlog']:
            zdaemon_conf.sections.append(event_log(event_log_path))

        # create zope.conf
        zope_conf_path = os.path.join(location, 'zope.conf')
        open(zope_conf_path, 'w').write(str(zope_conf))

        extra_paths = self.egg.extra_paths
        eggs, ws = self.egg.working_set()

        test_paths = [ws.find(pkg_resources.Requirement.parse(spec)).location
                      for spec in eggs]

        # setup start script
        defaults = options.get('defaults', '').strip()
        if defaults:
            defaults = '(%s) + ' % defaults

        initialization = initialization_template
        server_module = server_types[options['server']][0]

        dest.extend(zc.buildout.easy_install.scripts(
            [(options['script'], server_module, 'main')],
            ws, executable, self.buildout['buildout']['bin-directory'],
            extra_paths = extra_paths,
            arguments = defaults + (arg_template % dict(
                ZOPE_CONF=zope_conf_path,
                )),
            initialization = initialization,
            ))

        return dest

    update = install


site_zcml_template = """\
<configure
    xmlns="http://namespaces.zope.org/zope">

%s

</configure>
"""

principals_zcml_template = """\
<configure
    xmlns="http://namespaces.zope.org/zope">

%s

</configure>
"""

securitypolicy_zcml_template = """\
<configure
    xmlns="http://namespaces.zope.org/zope"
    i18n_domain="zope">

%s

</configure>
"""

arg_template = """[
  '-C', %(ZOPE_CONF)r,
  ]+sys.argv[1:]"""


initialization_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""

server_template = """
<server>
  type HTTP
  address %s
</server>
"""

access_log_template = """
<accesslog>
  <logfile>
    path %s
  </logfile>
</accesslog>
"""

event_log_template = """
<eventlog>
  <logfile>
    path %s
    formatter zope.exceptions.log.Formatter
  </logfile>
</eventlog>
"""

def access_log(path):
    return ZConfig.schemaless.Section(
        'accesslog', '',
        sections=[ZConfig.schemaless.Section('logfile', '', dict(path=[path]))]
        )

def event_log(path, *data):
    return ZConfig.schemaless.Section(
        'eventlog', '', None,
        [ZConfig.schemaless.Section(
             'logfile',
             '',
             dict(path=[path])),
         ])
