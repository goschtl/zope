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

import logging, os, re, shutil
from xml.sax.saxutils import quoteattr

import pkg_resources

import zc.buildout
import zc.recipe.egg

logger = logging.getLogger('zc.recipe.zope3instance')

class Recipe:
    # Need to think about the inheritence interface
    # it *is* reasonable to think about instances as an
    # extension of the basic egg/script-generation model.

    def __init__(self, buildout, name, options):
        self.options, self.name = options, name
        

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        
        options['zope3-location'] = buildout[options.get('zope3', 'zope3')
                                             ]['location']

        if len(options['user'].split(':')) not in (2,3):
            logger.error(
                "The user option must specify a login name,"
                " a password manager and a password.")
            raise UserError("Invalud user, %r", options['user'])

        options['database-config'] = '\n'.join([
            buildout[section]['zconfig']
            for section in options['database'].split()
            ])

        options['bin-directory'] = buildout['buildout']['bin-directory']

        zope_options = {}
        for option in options.get('zope-options', '').split('\n'):
            option = option.strip()
            if not option:
                continue
            option = option.split(' ', 1)
            if (len(option) == 1) or not option[1].strip():
                logger.error('%s: zope-option, %s, has no value',
                             self.name, option[0]
                             )
                raise zc.buildout.UserError("Invalid zope-option", option[0])
            zope_options[option[0]] = option[1]

        if 'interrupt-check-interval' not in zope_options:
            zope_options['interrupt-check-interval'] = '200'
            
        self.zope_options = zope_options

        # Let the egg recipe do much of the heavy lifting.
        options['scripts'] = ''
        options.pop('entry-points', None)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options

        z3path = options['zope3-location']
        if not os.path.exists(z3path):
            raise zc.buildout.UserError("No directory:", z3path)

        path = os.path.join(z3path, 'lib', 'python')
        if not os.path.exists(path):
            path = os.path.join(z3path, 'src')
            if not os.path.exists(path):
                logger.error(
                    "The directory, %r, isn't a valid checkout or release."
                    % z3)
                raise zc.buildout.UserError(
                    "Invalid Zope 3 installation:", z3path)

        extra = options.get('extra-paths')
        if extra:
            extra += '\n' + path
        else:
            extra = path
        options['extra-paths'] = extra

        skel = os.path.join(z3path, 'zopeskel', 'etc')
        if not os.path.exists(skel):
            logger.error("%r does not exists.", skel)
            raise UserError("Invalid Zope 3 Installation", src)


        dest = options['location']
        log_dir = run_dir = subprogram_dir = config_dir = dest
        requirements, ws = self.egg.working_set()

        os.mkdir(dest)

        site_zcml_path = os.path.join(config_dir, 'site.zcml')

        zope_options = self.zope_options
        zope_options['site-definition'] = site_zcml_path
        
        zope_options = '\n  '.join([
            ' '.join(option)
            for option in zope_options.iteritems()
            ])

        addresses = options.get('address', '8080').split()
        for address in addresses:
            zope_options += server_template % address

        # Install zope.conf        
        zope_conf_path = os.path.join(config_dir, 'zope.conf')
        open(zope_conf_path, 'w').write(zope_conf_template % dict(
            options = zope_options,
            database = options['database-config'],
            log_dir = log_dir,
            config = options['config'],
            ))

        # Install zdaemon.conf
        zdaemon_conf_path = os.path.join(config_dir, 'zdaemon.conf')
        open(zdaemon_conf_path, 'w').write(zdaemon_conf_template % dict(
            subprogram_dir = subprogram_dir,
            log_dir = log_dir,
            run_dir = run_dir,
            user = ''
            ))

        # Install zcml files
        self._zcml(options['zope3-location'], config_dir, options)

        # install subprohrams and ctl scripts
        zc.buildout.easy_install.scripts(
            [('runzope', 'zope.app.twisted.main', 'main')],
            ws, options['executable'], subprogram_dir,
            extra_paths = options['extra-paths'].split(),
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zope_conf_path),
            )

        # Install the scripts defined by this recipe, which adds entry points
        # missing frm Zope itself.
        requirements, ws = self.egg.working_set(['zc.recipe.zope3instance'])
        zc.buildout.easy_install.scripts(
            [('debugzope', 'zc.recipe.zope3instance.zope3scripts', 'debug'),
             ('scriptzope', 'zc.recipe.zope3instance.zope3scripts', 'script'),
             ],
            ws, options['executable'], subprogram_dir,
            extra_paths = options['extra-paths'].split(),
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zope_conf_path),
            )

        zc.buildout.easy_install.scripts(
            [(self.name, 'zc.recipe.zope3instance.ctl', 'main')],
            ws, options['executable'], options['bin-directory'],
            extra_paths = options['extra-paths'].split(),
            arguments = ('\n        %r,'
                         '\n        %r,'
                         '\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % (os.path.join(subprogram_dir, 'debugzope'),
                            os.path.join(subprogram_dir, 'scriptzope'),
                            zdaemon_conf_path)
                         ),
            )

        return dest, os.path.join(options['bin-directory'], self.name)

    def _zcml(self, src, dest, options):
        skel = os.path.join(src, 'zopeskel', 'etc')
        for name in os.listdir(skel):
            if name.endswith(".zcml"):
                shutil.copy(os.path.join(skel, name), dest)

        pzi = os.path.join(skel, 'principals.zcml.in')
        if os.path.exists(pzi):
            userdata = options['user'].split(':')
            if len(userdata) == 2:
                login, pw = userdata
                pwmanager = "Plain Text"
            else:
                login, pwmanager, pw = userdata
                
            open(os.path.join(dest, 'principals.zcml'), 'w').write(
                open(pzi).read()
                .replace('<<USERNAME-XMLATTR>>', quoteattr(login))
                .replace('<<PASSWORD_MANAGER>>', pwmanager)
                .replace('<<PASSWORD-XMLATTR>>', quoteattr(pw))
                )
            
        # add zcml files to package-includes
        zcml = options['zcml'] or '*' # Require zcml but allow it to be empty
        package_includes = os.path.join(dest, 'package-includes')
        if zcml:
            zcml = zcml.split()
            if '*' in zcml:
                zcml.remove('*')
                shutil.copytree(os.path.join(skel, 'package-includes'),
                                package_includes)
            else:
                os.mkdir(package_includes)

            n = 0
            package_match = re.compile('\w+([.]\w+)*$').match
            for package in zcml:
                n += 1
                orig = package
                if ':' in package:
                    package, filename = package.split(':')
                else:
                    filename = None

                if '-' in package:
                    package, suff = package.split('-')
                    if suff not in ('configure', 'meta', 'overrides'):
                        raise ValueError('Invalid zcml', orig)
                else:
                    suff = 'configure'

                if filename is None:
                    filename = suff + '.zcml'

                if not package_match(package):
                    raise ValueError('Invalid zcml', orig)

                path = os.path.join(
                    package_includes,
                    "%3.3d-%s-%s.zcml" % (n, package, suff),
                    )
                open(path, 'w').write(
                    '<include package="%s" file="%s" />\n'
                    % (package, filename)
                    )
        
    def update(self):
        pass



zope_conf_template = """\
# This is the configuration file for the Zope Application Server.
#
# This file is generated.  If you edit this file, your edits could
# easily be lost.

%(options)s

%(database)s

<accesslog>
  <logfile>
    path %(log_dir)s/access.log
  </logfile>

  <logfile>
    path STDOUT
  </logfile>
</accesslog>

<eventlog>
  <logfile>
    path %(log_dir)s/z3.log
    formatter zope.exceptions.log.Formatter
  </logfile>
  <logfile>
    path STDOUT
    formatter zope.exceptions.log.Formatter
  </logfile>
</eventlog>

%(config)s
"""

zdaemon_conf_template = """\
# Configuration file for the daemon that manages a Zope 3 process
#
# This file is generated.  If you edit this file, your edits could
# easily be lost.
<runner>
  program %(subprogram_dir)s/runzope
  %(user)sdaemon on
  transcript %(log_dir)s/transcript.log
  socket-name %(run_dir)s/zopectlsock
</runner>

<eventlog>
  <logfile>
    path %(log_dir)s/z3.log
  </logfile>
</eventlog>
"""

server_template = """
<server>
  type HTTP
#  type PostmortemDebuggingHTTP
  address %s
</server>
"""
