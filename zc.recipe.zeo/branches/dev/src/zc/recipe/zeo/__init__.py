import re, os, logging
import zc.buildout.easy_install
import zc.recipe.egg

start_section = re.compile('(^|\n)[ \t]*<[^>]+>[ \t]*\n').search
end_section = re.compile('(^|\n)[ \t]*</[^>]+>[ \t]*\n').search

logger = logging.getLogger('zc.recipe.zeo')

class Instance:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options
        
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        zeo_options = {}
        for option in options.get('zeo-options', '').split('\n'):
            option = option.strip()
            if not option:
                continue
            option = option.split(' ', 1)
            if (len(option) == 1) or not option[1].strip():
                logger.error('%s: zeo-option, %s, has no value',
                             self.name, option[0]
                             )
                raise zc.buildout.UserError("Invalid zeo-option", option[0])
            zeo_options[option[0]] = option[1]

        if 'address' not in zeo_options:
            zeo_options['address'] = '8100'

        self.zeo_options = '\n  '.join([
            ' '.join(option)
            for option in zeo_options.iteritems()
            ])

        dbconfig = buildout[options['database']]['zconfig']
        dbconfig = dbconfig[start_section(dbconfig).end(0):]
        dbconfig = dbconfig[start_section(dbconfig).start(0):]
        dbconfig = dbconfig[:end_section(dbconfig).end(0):]
        dbconfig = dbconfig.replace('>', ' 1>', 1)
        options['database-config'] = dbconfig

        zeo = options.get('zeo', 'ZODB3')
        zdaemon = options.get('zdaemon', 'ZODB3')
        if zdaemon != zeo:
            zeo += '\n' + zdaemon
        options['eggs'] = zeo

        options['bin-directory'] = buildout['buildout']['bin-directory']

        options['zconfig'] = zeoclient_template % dict(
            address = zeo_options['address'],
            )

        # We don't want scripts generated
        options['scripts'] = ''
        options.pop('entry-points', None)

        # delegate to egg recipe
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options
        dest = options['location']
        os.mkdir(dest)
        conf_path = os.path.join(dest, 'zeo.conf')

        # Later we'll use the deployment mechanism to get these:
        bin_dir = options['bin-directory']
        log_dir = dest
        subprogram_dir = dest
        run_dir = dest
        user = ''

        open(conf_path, 'w').write(
            zeo_conf % dict(
            options = self.zeo_options,
            storage = options['database-config'],
            log_dir = log_dir,
            subprogram_dir = subprogram_dir,
            run_dir = run_dir,
            user = user,
            executable = options['executable'],
            ))

        requirements, ws = self.egg.working_set()
            
        zc.buildout.easy_install.scripts(
            [('runzeo', 'ZEO.runzeo', 'main')],
            ws, options['executable'], subprogram_dir,
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % conf_path),
            )

        zc.buildout.easy_install.scripts(
            [('zdrun', 'zdaemon.zdrun', 'main')],
            ws, options['executable'], subprogram_dir,
            )
            
        zc.buildout.easy_install.scripts(
            [(self.name, 'ZEO.zeoctl', 'main')],
            ws, options['executable'], options['bin-directory'],
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % conf_path),
            )        

        return dest, os.path.join(bin_dir, self.name)
        
    def update(self):
        pass


zeo_conf = """\
# ZEO configuration file
#
# This file is generated.  If you edit this file, your edits could
# easily be lost.

<zeo>
  %(options)s
</zeo>

%(storage)s

<eventlog>
  level info
  <logfile>
    path %(log_dir)s/zeo.log
  </logfile>
</eventlog>

<runner>
  program %(subprogram_dir)s/runzeo
  socket-name %(run_dir)s/zeo.zdsock
  daemon true
  forever false
  backoff-limit 10
  exit-codes 0, 2
  directory %(run_dir)s
  default-to-interactive true
  %(user)spython %(executable)s
  logfile %(log_dir)s/zeo.log
</runner>
"""

zeoclient_template = """\
<zodb>
  <zeoclient>
     server %(address)s
  </zeoclient>
</zodb>
"""
