import sys, os
import urllib2
import simplejson

YUILOADER_URL_TEMPLATE = ('http://yui.yahooapis.com/%s/build/yuiloader'
                          '/yuiloader-beta.js')

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: yuidepend <YUI version>"
        return
    d = load_json(version)

    items = sorted_dependencies(d)
    
    resources_text = []
    for key, value in items:
        path = deminize(value['path'])
        name = normalize_name(key)
        resource = '%s_resource = ResourceSpec(yui,\n    "%s"' % (
            name, path)
        
        modes = get_modes(path)
        if modes:
            for key, mode_path in sorted(modes.items()):
                resource += ',\n    %s="%s"' % (key, mode_path)
        resource += ')'
        resources_text.append(resource)

    resources_text = '\n'.join(resources_text)
    
    inclusions_text = []
    for key, value in items:
        name = normalize_name(key)
        inclusion = '%s = Inclusion([%s_resource]' % (
            name, name)
        requires = value.get('requires', [])
        if requires:
            requires = [normalize_name(n) for n in requires]
            depends_on = '[%s]' % (', '.join(requires))
            inclusion += ', depends_on=%s' % depends_on
        
        inclusion += ')'
        inclusions_text.append(inclusion)
        
    inclusions_text = '\n'.join(inclusions_text)

    python = """\
from hurry.resource import Library, Inclusion, ResourceSpec

yui = Library('yui')

%s

%s
""" % (resources_text, inclusions_text)
    print python

def normalize_name(n):
    return n.replace('-', '_')

def deminize(path):
    rest, ext = os.path.splitext(path)
    if rest.endswith('-min'):
        rest = rest[:-len('-min')]
    return rest + ext

def get_modes(path):
    rest, ext = os.path.splitext(path)
    if ext == '.css':
        return {'minified': rest + '-min' + ext}
    elif ext == '.js':
        return {'minified': rest + '-min' + ext,
                'debug': rest + '-debug' + ext}
    else:
        return {}
    
def sorted_dependencies(d):
    """Given dictionary created sorted list of items.

    Sort by how much we depend.
    """
    # count dependencies of each item
    depend_sortkey = {}
    for key, value in d.items():
        for r in value.get('requires', []):
            c = depend_sortkey.get(r, 0)
            c += 1
            depend_sortkey[r] = c

    # add up numbers of dependencies
    depend_sortkey2 = {}
    for key, value in d.items():
        v = depend_sortkey.get(key, 0)
        for r in value.get('requires', []):
            c = depend_sortkey2.get(r, 0)
            c += v
            depend_sortkey2[r] = c

    # sort items by consolidated sort key
    items = d.items()
    items = sorted(items, key=lambda (key, value):
                   depend_sortkey2.get(key, 0))
    # reverse result so that things depended on most appear first
    return list(reversed(items))

def load_json(version):
    f = urllib2.urlopen(YUILOADER_URL_TEMPLATE % version)
    data = f.read()
    f.close()
    s = "'moduleInfo': "
    i = data.find(s)
    i = i + len(s)
    j = data.find("'yuitest': {", i)
    j = data.find('}', j)
    j = data.find('}', j + 1)
    text = data[i:j + 1]
    json = normalize_json(text)
    return simplejson.loads(json)

def normalize_json(text):
    # proper json has doubly quoted strings
    text = text.replace("'", '"')
    result = []
    for line in text.splitlines():
        i = line.find('//')
        if i != -1:
            line = line[:i] + '\n'
        result.append(line)
    return ''.join(result)
