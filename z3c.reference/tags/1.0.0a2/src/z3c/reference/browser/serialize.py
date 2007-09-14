import cElementTree
import urllib

from BeautifulSoup import BeautifulSoup


def serializeForm(html):
    tags = BeautifulSoup(html)(['input', 'textarea'])
    html = ''.join([unicode(tag) for tag in tags])
    html = '<div>%s</div>' % html
    elem = cElementTree.fromstring(html.encode('utf-8'))
    res = []
    for e in elem.findall('input'):
        name = e.get('name')
        value = e.get('value').encode('utf-8')
        t = e.get('type')
        if (   t not in ('hidden', 'text')
            or None in (name, value)
           ):
            continue
        res.append((name, value))
    for e in elem.findall('textarea'):
        name = e.get('name')
        value = e.text or ''
        if name is None:
            continue
        res.append((name, value.encode('utf-8')))
    return urllib.urlencode(res)

