
class GoogleAnalytics(object):

    def __call__(self):
        if "zboiler.com" in self.request.getURL():
            return super(GoogleAnalytics, self).__call__()
        return "<!-- google analytics here when on zboiler.com -->"
