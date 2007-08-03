import re
import zope.publisher.browser

marker = object()
# lifted from ZPublisher.HTTPRequest
URLmatch = re.compile('URL(PATH)?([0-9]+)$').match
BASEmatch = re.compile('BASE(PATH)?([0-9]+)$').match

class BrowserRequest(zope.publisher.browser.BrowserRequest):

    def __init__(self, body_instream, environ, response=None):
        self.other = {}
        super(BrowserRequest, self).__init__(body_instream, environ, response)
        self.__setupLegacy()

    def __setupLegacy(self):
        self.other.update({
            'REQUEST': self,
            'PARENTS': [],    # TODO check if we remember all parents yet
            'BODYFILE': self.bodyStream,
            })

        #XXX
        self.maybe_webdav_client = False

    def get(self, key, default=None):
        if key in self.other:
            return self.other[key]

        if key == 'RESPONSE':
            return self.response

        # support URLn, URLPATHn
        if key.startswith('URL'):
            if key == 'URL':
                return self.getURL()
            match = URLmatch(key)
            if match is not None:
                pathonly, n = match.groups()
                # XXX is this correct?
                return self.getURL(int(n), pathonly)

        # support BASEn, BASEPATHn
        if key.startswith('BASE'):
            # XXX just 'BASE'???
            match = BASEmatch(key)
            if match is not None:
                pathonly, n = match.groups()
                # XXX I have no clue what to return here
                return self.getURL(int(n), pathonly)

        # support BODY
        #XXX

        return super(BrowserRequest, self).get(key, default)

    def keys(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        keys = set(self._environ.keys() + self._cookies.keys()
                   + self.form.keys() + self.other.keys())
        # TODO URLn, URLPATHn, BASEn, BASEPATHn
        keys.update(['URL', 'RESPONSE'])
        return list(keys)

    # BBB discouraged methods:

    def __setitem__(self, key, value):
        self.other[key] = value

    set = __setitem__

    def __getattr__(self, key, default=marker):
        value = self.get(key, default)
        if value is marker:
            raise AttributeError(key)
        return value
