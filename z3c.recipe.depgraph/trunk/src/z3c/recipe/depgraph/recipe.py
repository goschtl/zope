import os

from zc.buildout import easy_install
from zc.recipe.egg import Egg

EXCLUDE_PACKAGES = set((
    'lxml',
    'pytz',
    'setuptools',
    'tl.eggdeps',
    'z3c.recipe.depgraph',
    'zc.buildout',
    'zc.recipe.egg',
))


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.egg = Egg(buildout, options['recipe'], options)
        exclude = self.options.get('exclude', '')
        self.exclude = set(exclude.split())
        self.output = self.options.get(
            'output', os.path.join(
            self.buildout['buildout']['parts-directory'], self.name))
        extras = self.options.get('extras', 'false')
        self.extras = extras.lower() in ('1', 'true', 'yes')

    def install(self):
        options = self.options
        reqs, ws = self.egg.working_set(['z3c.recipe.depgraph'])

        if not os.path.exists(self.output):
            os.mkdir(self.output)

        variants = options.get('variants', 'base tred scc')
        variants = [v.strip() for v in variants.split()]

        # Install an interpreter
        packages = set([dist.project_name for dist in ws.by_key.values()])
        packages = packages - EXCLUDE_PACKAGES - self.exclude
        packages = list(packages)

        # Allow to map distribution names to different package names
        pmap = dict()
        package_map = options.get('package-map', '').strip()
        if package_map:
            pmap = self.buildout[package_map]
        packages.sort()

        easy_install.scripts(
            [('graph-%s' % self.name, 'z3c.recipe.depgraph.runner', 'main')],
            ws, options['executable'], options['bin-directory'],
            arguments=dict(
                packages=packages,
                package_map=package_map,
                name=self.name,
                path=self.output,
                variants=variants,
                extras=self.extras,
                ),
            )

        reqs = ['tl.eggdeps']
        scripts = {
            'eggdeps' : '%s-eggdeps' % self.name
        }

        easy_install.scripts(
            reqs, ws, options['executable'], options['bin-directory'],
            scripts=scripts,
            )
        return self.output

    def update(self):
        self.install()
