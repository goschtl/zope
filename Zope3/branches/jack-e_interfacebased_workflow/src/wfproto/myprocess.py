from zope.event import notify

from userevent import UserEvent



class FormSubmitView:

    def __init__(self, context, request):
        self.context=context
        self.request=request

    # XXX easy way .. not final !!!
    def submit(self, transition):
        notify(UserEvent(self.context, transition, self.request.form))
        
        # XXX how do we control this ??
        self.request.response.redirect(self.request.get('REFERER', '') or 'wfproto.html')
