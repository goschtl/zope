import os

GENERATE = "./bin/%(scriptname)s -x -d %(package)s -i setuptools > %(output)s"
TRED = "tred %(input)s > %(output)s"
GRAPH = "dot -Tsvg %(input)s > %(output)s"

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

        execute(TRED,
            input=specfile + '.dot',
            output=specfile + '-tred.dot')

        execute(GRAPH,
            input=specfile + '-tred.dot',
            output=specfile + '-tred.svg')
