import os

GENERATE = "./bin/%(scriptname)s -x -d %(package)s -i setuptools > %(output)s"
TRED = "tred %(input)s > %(output)s"
GRAPH = "dot -Tsvg %(input)s > %(output)s"
SCCMAP = "sccmap -d %(input)s > %(output)s"
SCCGRAPH = "dot -Tsvg %(input)s -O"

PACKAGE_EXCEPTIONS = {
    'Plone' : 'Products.CMFPlone',
}

def execute(template, **kwargs):
    os.system(template % kwargs)


def main(args):
    name = args.get('name')
    packages = args.get('packages')
    path = args.get('path')
    scriptname = name + '-eggdeps'
    variants = args.get('variants', ['base', 'tred', 'scc'])

    for package in packages:
        package = PACKAGE_EXCEPTIONS.get(package, package)
        deeppath = os.path.join(path, package.replace('.', os.sep))

        if not os.path.exists(deeppath):
            os.makedirs(deeppath)

        specfile = os.path.join(deeppath, 'spec')
        execute(GENERATE,
            scriptname=scriptname,
            package=package,
            output=specfile + '.dot')

        execute(GRAPH,
            input=specfile + '.dot',
            output=specfile + '.svg')

        if 'tred' in variants:
            execute(TRED,
                input=specfile + '.dot',
                output=specfile + '-tred.dot')

            execute(GRAPH,
                input=specfile + '-tred.dot',
                output=specfile + '-tred.svg')

        if 'scc' in variants:
            execute(SCCMAP,
                input=specfile + '.dot',
                output=specfile + '-sccmap')

            execute(SCCGRAPH,
                input=specfile + '-sccmap')
