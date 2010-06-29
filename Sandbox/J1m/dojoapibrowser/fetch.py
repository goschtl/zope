import BeautifulSoup
import json
import os
import sys
import urllib2

class Node(dict):

    def __init__(self, label, url, id):
        assert isinstance(label, unicode)
        self.label = label
        self.url = url
        self.id = id

def links():
    nnodes = 0
    root = Node(u'Dojo toolkit API', '/api', 'root')
    for top in 'dojo', 'dijit', 'dojox', 'djConfig':
        f = urllib2.urlopen('http://dojotoolkit.org/api/%s.html' % top)
        soup = BeautifulSoup.BeautifulSoup(f.read())
        f.close()
        prefix = '/api/%s/' % top
        for a in soup.findAll('a', **{'class': 'jsdoc-link'}):
            href = a['href']
            if not href.startswith(prefix):
                continue
            if not href.endswith('.html'):
                continue
            names = href[5:-5].split('/')
            node = root
            url = root.url
            for n in names:
                url += '/'+n
                if n not in node:
                    nnodes += 1
                    node[n] = Node(n, url+'.html', 'n%s' % nnodes)
                node = node[n]
            node.label = u''.join(a.contents)
            node.url = href

    result = dict(identifier='id', label='label',
                  items = [d for d in flatten(root)])
    result = json.dumps(result)
    return result

def flatten(node):
    data = dict(
        id=node.id, url=node.url,
        label=node.label,
        )
    if node:
        children = sorted(node.values(), key=lambda n: n.label.lower())
        goofy_prefix = node.label + '._'
        goofy = [n for n in children if n.label.startswith(goofy_prefix)]
        if goofy:
            children = [dict(_reference=n.id)
                        for n in children
                        if not n.label.startswith(goofy_prefix)]
            goofy = dict(
                label = 'underware',
                id=node.id+'goofy',
                url='',
                children=[dict(_reference=n.id) for n in goofy]
                )
            children.append(dict(_reference=goofy['id']))
            yield goofy
            data['children'] = children
        else:
            data['children'] = [dict(_reference=n.id) for n in children]
    yield data
    for n in sorted(node):
        for data in flatten(node[n]):
            yield data

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    out, = args
    open(out, 'w').write(links())

if __name__ == '__main__':
    main(['api.json'])
