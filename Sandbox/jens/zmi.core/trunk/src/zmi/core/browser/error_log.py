from .base import ZMIView
from .base import Message as _


class ErrorLogView(ZMIView):

    def __call__(self, SAVE=None, FORGET=None, REFRESH=None, keep_entries=0,
                  copy_to_zlog=0, ignored_exceptions=(), id=None):
        if SAVE:
            self.context.setProperties(keep_entries, copy_to_zlog,
                                       ignored_exceptions)
            self.status = _(u'Changed properties.')
            return self.redirect()
        elif FORGET:
            self.context.forgetEntry(id)
            self.status = _(u'Error log entry was removed.')
            return self.redirect()
        elif REFRESH:
            return self.redirect()
        return self.index()

    @property
    def entry_url(self):
        return '%s/@@zmi_error_log_entry?id=' % self.context.absolute_url()

    @property
    def forget_url(self):
        return '%s?FORGET=True&id=' % self.request.ACTUAL_URL
