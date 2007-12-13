import os

exclude = ['slapd', 'conf', 'urls', 'use-socket', 'recipe',
           'location', 'executable', 'bin-directory',
           'eggs-directory', 'develop-eggs-directory', 'find-links',
           '_e', '_d', '_b']
paths = ['include', 'pidfile', 'argsfile', 'modulepath', 'directory']
multiple = ['include', 'access', 'moduleload', 'dbconfig', 'index']
defaults = [('include', '/etc/openldap/schema/core.schema'),
            ('modulepath', '/usr/lib/openldap'),
            ('moduleload', 'back_bdb'),
            ('database', 'bdb'),
            ('dbconfig', ('set_cachesize\t0\t268435456\t1\n'
                          'set_lg_regionmax\t262144\n'
                          'set_lg_bsize\t2097152')),
            ('index', 'objectClass\teq')]
order = ['include', 'pidfile', 'argsfile', 'access', 'modulepath',
         'moduleload', 'database', 'suffix', 'directory', 'dbconfig',
         'index']

def init_options(options, dir='.', exclude=exclude,
                      paths=paths, multiple=multiple,
                      defaults=defaults):
    for key, value in defaults:
        if key not in options:
            options[key] = value

    for key, value in options.iteritems():
        value = value.strip()
        if not value:
            del options[key]
            continue
        if key in exclude:
            continue

        if key in multiple:
            values = []
            for v in value.split('\n'):
                v = v.strip()
                if not v:
                    continue
                if key in paths:
                    # expand file paths
                    v = os.path.join(dir, v)
                values.append(v)
            options[key] = '\n'.join(values)
            continue

        if key in paths:
            options[key] = os.path.join(dir, value)

def order_keys(keys, order=order):
    for key in order:
        if key in keys:
            yield key
    for key in keys:
        if key not in order:
            yield key

def get_lines(options, exclude=exclude,
                   multiple=multiple, template='%s\t%s\n'):
    for key in order_keys(options):
        if key in exclude:
            continue

        value = options[key]
        if key in multiple:
            for v in value.split('\n'):
                yield template % (key, v)
        else:
            yield template % (key, value)
