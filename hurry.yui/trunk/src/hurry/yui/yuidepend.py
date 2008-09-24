import sys, os
import urllib2
import simplejson

from hurry.resource import Library, ResourceInclusion, generate_code

YUILOADER_URL_TEMPLATE = ('http://yui.yahooapis.com/%s/build/yuiloader'
                          '/yuiloader-beta.js')

def main():
    try:
        version = sys.argv[1]
    except IndexError:
        print "Usage: yuidepend <YUI version>"
        return
    d = load_json(version)
    
    convert_to_inclusions(d)

def convert_to_inclusions(d):
    yui = Library('yui')
    inclusion_map = {}
    for name, value in d.items():
        name = normalize_name(name)
        inclusion_map[name] = ResourceInclusion(yui,
                                                deminize(value['path']))

    # fix up dependency structure, rollups
    for name, value in d.items():
        name = normalize_name(name)
        inclusion = inclusion_map[name]
        require_inclusions = []
        for require in value.get('requires', []):
            require = normalize_name(require)
            require_inclusions.append(inclusion_map[require])
        inclusion.depends = require_inclusions
        rollup_inclusions = []
        for rollup_name in value.get('supersedes', []):
            rollup_name = normalize_name(rollup_name)
            r = inclusion_map[rollup_name]
            rollup_inclusion = ResourceInclusion(
                yui, r.relpath)
            rollup_inclusions.append(rollup_inclusion)
        inclusion.rollups = rollup_inclusions
        mode_inclusions = {}
        for mode_name, path in get_modes(inclusion.relpath).items():
            mode_inclusions[mode_name] = ResourceInclusion(
                yui, path) # XXX rollups
        inclusion.modes = mode_inclusions
        
    # now generate code
    print generate_code(**inclusion_map)
    
def normalize_name(n):
    return str(n.replace('-', '_'))

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
