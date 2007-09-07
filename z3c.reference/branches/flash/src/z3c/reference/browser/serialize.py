import cElementTree
import urllib
def serializeForm(html):

    html = '<div>%s</div>' % html
    elem = cElementTree.fromstring(html)
    res = []
    for e in elem.findall('input'):
        name = e.get('name')
        value = e.get('value')
        t = e.get('type')
        if t not in ('hidden', 'text') or None in (name, value):
            continue
        res.append((name, value))
    for e in elem.findall('textarea'):
        name = e.get('name')
        value = e.text or ''
        if name is None:
            continue
        res.append((name, value))
    return urllib.urlencode(res)

