from zope.app.publisher.browser.viewmeta import page
from optionstorage.browser import OptionStorageView

class optionStorage(object):

    def __init__(self, _context, class_=None, **kwargs):
        self._context = _context
        self.class_ = class_
        self.opts = kwargs.copy()
        self.dictlist = []

    def options(self, _context, name, topic):
        self.dictlist.append((name, topic))

    def __call__(self):
        class_ = self.class_
        if class_ is None:
            class_ = OptionStorageView
        class_ = type("OptionStorageView", (class_,),
                      {"dictlist": self.dictlist})
        page(self._context, class_=class_, **self.opts)
        return ()
