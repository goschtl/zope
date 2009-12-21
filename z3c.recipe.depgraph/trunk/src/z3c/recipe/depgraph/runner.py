import os

GENERATE = "./bin/%(scriptname)s %(exclude)s %(re_exclude)s %(dead_ends)s %(re_dead_ends)s %(extras)s-d \"%(package)s\" -i setuptools > %(output)s"
TRED = "tred %(input)s > %(output)s"
GRAPH = "dot -T%(format)s %(input)s > %(output)s"
SCCMAP = "sccmap %(input)s > %(output)s"
SCCGRAPH = "dot -T%(format)s %(input)s -O"


def execute(template, **kwargs):
    os.system(template % kwargs)


def build_option(option, pattern):
    result = ''
    for i in pattern:
        result += '%s %s ' % (option, i)
    return result


def main(args):
    name = args.get('name')
    packages = args.get('packages')
    package_map = args.get('package_map')
    path = args.get('path')
    scriptname = name + '-eggdeps'
    variants = args.get('variants', ['base', 'tred', 'scc'])
    formats = args.get('formats', ['svg'])
    extras = args.get('extras')
    exclude = build_option('-i', args.get('exclude'))
    re_exclude = build_option('-I', args.get('re_exclude'))
    dead_ends = build_option('-e', args.get('dead_ends'))
    re_dead_ends = build_option('-E', args.get('re_dead_ends'))

    for package in packages:
        name = package.split('[', 1)[0].strip()
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
            exclude=exclude,
            re_exclude=re_exclude,
            dead_ends=dead_ends,
            re_dead_ends=re_dead_ends,
            output=specfile + '.dot')

        for format in formats:
            execute(GRAPH,
                format=format,
                input=specfile + '.dot',
                output=specfile + '.%s' % format)

        if 'tred' in variants:
            execute(TRED,
                input=specfile + '.dot',
                output=specfile + '-tred.dot')

            for format in formats:
                execute(GRAPH,
                    format=format,
                    input=specfile + '-tred.dot',
                    output=specfile + '-tred.%s' % format)

        if 'scc' in variants:
            execute(SCCMAP,
                input=specfile + '.dot',
                output=specfile + '-sccmap')

            for format in formats:
                execute(SCCGRAPH,
                    format=format,
                    input=specfile + '-sccmap')
