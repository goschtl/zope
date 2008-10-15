import sys, os
import urllib2
import simplejson

from hurry.resource import Library, ResourceInclusion, generate_code

YUILOADER_BETA_URL_TEMPLATE = ('http://yui.yahooapis.com/%s/build/yuiloader'
                               '/yuiloader-beta.js')

YUILOADER_URL_TEMPLATE = ('http://yui.yahooapis.com/%s/build/yuiloader'
                         '/yuiloader.js')

def depend(version):
    d = load_json(version)
    return convert_to_inclusions(d)

def convert_to_inclusions(d):
    yui = Library('yui')
    inclusion_map = {}
    for name, value in d.items():
        name = normalize_name(name)
        inclusion_map[name] = ResourceInclusion(yui,
                                                deminize(value['path']))
                
    # fix up dependency structure
    # XXX note that this doesn't establish proper rollup backreferences
    # but this doesn't matter as we're just going to generate the
    # code that does...
    for name, value in d.items():
        name = normalize_name(name)
        inclusion = inclusion_map[name]

        for require in value.get('requires', []):
            require = normalize_name(require)
            inclusion.depends.append(inclusion_map[require])

        for supersede_name in value.get('supersedes', []):
            orig_supersede_name = supersede_name
            supersede_name = normalize_name(supersede_name)
            r = inclusion_map[supersede_name]
            # only supersede things that don't supersede themselves
            if not d[orig_supersede_name].get('supersedes'):
                inclusion.supersedes.append(r)

        for mode_name in get_modes(inclusion):
            inclusion.modes[mode_name] = mode_inclusion = convert_to_mode(
                inclusion, mode_name)

    # now generate code
    return generate_code(**inclusion_map)
    
def normalize_name(n):
    return str(n.replace('-', '_'))

def deminize(path):
    rest, ext = os.path.splitext(path)
    if rest.endswith('-min'):
        rest = rest[:-len('-min')]
    return rest + ext

def convert_to_mode(inclusion, mode):
    rest, ext = os.path.splitext(inclusion.relpath)
    if mode == 'minified' and not inclusion.supersedes:
        result = ResourceInclusion(inclusion.library,
                                   rest + '-min' + ext)
    elif mode == 'debug' and not inclusion.supersedes:
        result = ResourceInclusion(inclusion.library,
                                   rest + '-debug' + ext)
    else:
        result = inclusion
        
    return result

def get_modes(inclusion):
    ext = inclusion.ext()
    if ext == '.css':
        return ['minified']
    elif ext == '.js':
        return ['minified', 'debug']
    else:
        return []
    
def load_json(version):
    try:
        f = urllib2.urlopen(YUILOADER_URL_TEMPLATE % version)
        data = f.read()
        f.close()
    except urllib2.HTTPError:
        f = urllib2.urlopen(YUILOADER_BETA_URL_TEMPLATE % version)
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
