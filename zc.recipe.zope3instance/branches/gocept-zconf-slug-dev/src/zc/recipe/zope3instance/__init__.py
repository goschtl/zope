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
        self.options = options
        self.name = name

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        options['skeleton'] = os.path.join(
            buildout['buildout']['directory'],
            'skels', name)

        options['zope3-location'] = buildout[options.get('zope3', 'zope3')
                                             ]['location']

        options['database-config'] = '\n'.join([
            buildout[section]['zconfig']
            for section in options['database'].split()
            ])

        options['bin-directory'] = buildout['buildout']['bin-directory']

        # Let the egg recipe do much of the heavy lifting.
        options['scripts'] = ''
        options.pop('entry-points', None)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options

        z3path = self._validateZ3Path(options['zope3-location'])

        extra = options.get('extra-paths')
        if extra:
            extra += '\n' + z3path
        else:
            extra = z3path
        options['extra-paths'] = extra

        # Compute various paths
        dest = options['location']
        zope_conf_path = os.path.join(dest, 'zope.conf')
        zdaemon_conf_path = os.path.join(dest, 'zdaemon.conf')

        for dir in ['log_dir', 'run_dir', 'subprogram_dir', 'config_dir']:
            if not options.has_key(dir):
                options[dir] = dest

        options['site_zcml_path'] = os.path.join(options['config_dir'], 'site.zcml')

        # XXX In theory we could just delete the parts directory here, if it
        # exists already. Or not?
        os.mkdir(dest)


        requirements, ws = self.egg.working_set()

        # install subprograms and ctl scripts
        zc.buildout.easy_install.scripts(
            [('runzope', 'zope.app.twisted.main', 'main')],
            ws, options['executable'], options['subprogram_dir'],
            extra_paths = options['extra-paths'].split(),
            arguments = ('\n        ["-C", %r]'
                         '\n        + sys.argv[1:]'
                         % zope_conf_path),
            )

        # Install the scripts defined by this recipe, which adds entry points
        # missing from Zope itself.
        requirements, ws = self.egg.working_set(['zc.recipe.zope3instance'])
        zc.buildout.easy_install.scripts(
            [('debugzope', 'zc.recipe.zope3instance.zope3scripts', 'debug'),
             ('scriptzope', 'zc.recipe.zope3instance.zope3scripts', 'script'),
             ],
            ws, options['executable'], options['subprogram_dir'],
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
                         % (os.path.join(options['subprogram_dir'], 'debugzope'),
                            os.path.join(options['subprogram_dir'], 'scriptzope'),
                            zdaemon_conf_path)
                         ),
            )

        self.installSkeleton(options['skeleton'], options['config_dir'], options)
        return dest, os.path.join(options['bin-directory'], self.name)


    def installSkeleton(self, src, dest, options):
        """Installs ZCML and config files by using given skeletons
        and configuration data from buildout.

        """
        if not os.path.exists(dest):
            os.mkdir(dest)
        if not os.path.isdir(dest):
            raise Exception("%dest is not a directory.")

        # Copy skeletons
        for overlay in [os.path.join(os.path.dirname(__file__), 'skel'),
                src]:
            self._copy_skeleton(overlay, dest)

        self._update_infiles(dest, options)

    def _copy_skeleton(self, src, dest):
        """Copies a skeleton directory recursively."""
        # XXX Use pkg_resources to become zip_safe.
        for name in os.listdir(src):
            if name in ['.svn']:
                continue
            src_name = os.path.join(src, name)
            if os.path.isdir(src_name):
                dest_name = os.path.join(dest, name)
                os.mkdir(dest_name)
                self._copy_skeleton(src_name, dest_name)
            else:
                shutil.copy(src_name, dest)

    def _update_infiles(self, dest, options):
        """Update a tree of files by converting .in files to
        their configured counterparts.

        """
        for name in os.listdir(dest):
            in_file = os.path.join(dest, name)

            if os.path.isdir(in_file):
                # Recurse into directories
                return _update_infiles(in_file, options)
            if not name.endswith('.in'):
                continue

            new_name = os.path.join(dest, name[:-3])

            old_contents = file(in_file, 'r').read()
            new_contents = old_contents % options

            file(new_name, 'w').write(new_contents)
            os.remove(in_file)

    def _validateZ3Path(self, path):
        """Validate that a given absolute path is a Zope 3 installation or checkout.

        Return the path that should be added to the PYTHONPATH for the generated
        scripts.
        """
        def fail():
            logger.error(
                "The directory, %r, isn't a valid checkout or release."
                % path)
            raise zc.buildout.UserError(
                "Invalid Zope 3 installation: ", path)

            if not os.path.exists(path):
                raise zc.buildout.UserError("No directory:", path)

        # Check that either lib/python or src/ exists.
        choices = [('lib', 'python'), ('src',)]
        choices = map(lambda x:os.path.join(path, *x), choices)
        valid_paths = filter(os.path.exists, choices)
        if not valid_paths:
            fail()

        # Additionally zopeskel/etc must exist too.
        skel = os.path.join(path, 'zopeskel', 'etc')
        if not os.path.exists(skel):
            fail()
        return valid_paths[0]
