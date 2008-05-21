# Copied from zc/recipe/testrunner/__init__.py mostly.

import os
import zc.buildout.easy_install
import zc.recipe.egg


class Creator(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         options.get('script', self.name),
                                         )
        # The generated script needs our own recipe plus dependencies
        # in the path, which is neatly done with this call:
        self.egg = zc.recipe.egg.Egg(buildout, 'z3c.recipe.eggbasket', options)

    def install(self):
        options = self.options
        dest = []
        eggs, ws = self.egg.working_set()

        dest.extend(zc.buildout.easy_install.scripts(
            [(options['script'], 'z3c.recipe.eggbasket.utils',
              'create_source_tarball')],
            ws, options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            arguments = (arg_template % dict(
                        egg=options['egg'],
                        versionfile=options['versionfile'],
                        )),
            ))

        return dest

    update = install


arg_template = """
        egg = '%(egg)s',
        versionfile = '%(versionfile)s'"""
