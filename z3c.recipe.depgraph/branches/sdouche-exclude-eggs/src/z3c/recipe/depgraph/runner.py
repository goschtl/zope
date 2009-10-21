import os

GENERATE = "./bin/%(scriptname)s %(extras)s-d %(package)s -i setuptools > %(output)s"
TRED = "tred %(input)s > %(output)s"
GRAPH = "dot -Tsvg %(input)s > %(output)s"
SCCMAP = "sccmap %(input)s > %(output)s"
SCCGRAPH = "dot -Tsvg %(input)s -O"


def execute(template, **kwargs):
    os.system(template % kwargs)


def main(args):
    name = args.get('name')
    packages = args.get('packages')
    package_map = args.get('package_map')
    path = args.get('path')
    scriptname = name + '-eggdeps'
    variants = args.get('variants', ['base', 'tred', 'scc'])
    extras = args.get('extras')

    for package in packages:
        name = package
        if name in package_map:
            name = package_map[name]
        deeppath = os.path.join(path, name.replace('.', os.sep))

        if not os.path.exists(deeppath):
            os.makedirs(deeppath)

        if extras:
            extras = '-x '
        else:
            extras = ''

        specfile = os.path.join(deeppath, 'spec')
        execute(GENERATE,
            extras=extras,
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
