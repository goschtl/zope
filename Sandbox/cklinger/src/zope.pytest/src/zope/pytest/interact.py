import webob
import simplejson
import base64
from pprint import pformat
import urllib

def auth(username, password):
    auth = base64.encodestring('%s:%s' % (username, password))
    return 'Basic %s' % auth[:-1]

def get_interact_for_url(app, url):
    json = get_json(app, url)
    return Interact(app, json)

def get_json(app, url, username='mgr', passwd='mgrpw'):
    request = webob.Request.blank(url)
    request.headers['Content-Type'] = 'application/json'
    if username is not None:
        request.environ['HTTP_AUTHORIZATION'] = auth(username, passwd)
    response = request.get_response(app)
    return simplejson.loads(response.body)

def post_json(app, url, json, username='mgr', passwd='mgrpw'):
    request = webob.Request.blank(url)
    request.method = 'POST'
    request.headers['Content-Type'] = 'application/json'
    if username is not None:
        request.environ['HTTP_AUTHORIZATION'] = auth(username, passwd)
    request.body = simplejson.dumps(json)
    response = request.get_response(app)
    return simplejson.loads(response.body)

def normal_post(app, url, data, username, passwd):
    request = webob.Request.blank(url)
    request.method = 'POST'
    if username is not None:
        request.environ['HTTP_AUTHORIZATION'] = auth(username, passwd)
    request.body = urllib.urlencode(data)
    response = request.get_response(app)
    return simplejson.loads(response.body)


class Interact(object):
    def __init__(self, app, json):
        self.app = app
        self.json = json

    def __repr__(self):
        return pformat(self.json)

    def get_one(self, key, **kw):
        if isinstance(self.json, list):
            value = self.json[int(key)]
        else:
            value = self.json[key]
        if isinstance(value, basestring):
            if value.startswith('http://'):
                return self.get_url(value, **kw)
        return Interact(self.app, value)

    def get_url(self, url, **kw):
        if kw:
            url = url + '?' + urllib.urlencode(kw)
        return Interact(self.app, get_json(self.app, url))

    def get(self, key, **kw):
        steps = key.split('.')
        assert len(steps) >= 1
        interact = self
        for step in steps[:-1]:
            interact = interact.get_one(step)
        interact = interact.get_one(steps[-1], **kw)
        return interact

    def post_url(self, url, json, username='mgr', passwd='mgrpw'):
        return Interact(self.app, post_json(
            self.app, url, json, username, passwd))

    def normal_post_url(self, url, data, username='mgr', passwd='mgrpw'):
        return Interact(self.app, normal_post(
            self.app, url, data, username, passwd))

