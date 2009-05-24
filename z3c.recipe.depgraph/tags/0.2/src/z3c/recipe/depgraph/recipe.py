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

    def install(self):
        options = self.options
        reqs, ws = self.egg.working_set(['z3c.recipe.depgraph'])

        if not os.path.exists(self.output):
            os.mkdir(self.output)

        variants = options.get('variants', 'base tred scc')
        variants = [v.strip() for v in variants.split()]

        # Install an interpreter
        packages = set(ws.by_key.keys()) - EXCLUDE_PACKAGES - self.exclude
        packages = list(packages)
        packages.sort()
        easy_install.scripts(
            [('graph-%s' % self.name, 'z3c.recipe.depgraph.runner', 'main')],
            ws, options['executable'], options['bin-directory'],
            arguments=dict(
                packages=packages,
                name=self.name,
                path=self.output,
                variants=variants
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
