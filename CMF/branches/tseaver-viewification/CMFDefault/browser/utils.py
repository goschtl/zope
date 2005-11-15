from ZTUtils import make_query

from Products.CMFCore.utils import getToolByName


class FormViewBase:

    def __call__(self, change='', change_and_view=''):
        form = self.request.form
        for button in self._BUTTONS:
            if button['name'] in form:
                for transform in button['transform']:
                    if not getattr(self, transform)(**form):
                        return self.index()
                if self.setRedirect(*button['redirect']):
                    return
        return self.index()

    def listButtonInfos(self):
        return self._BUTTONS

    def setStatus(self, success, message='', **kw):
        if message:
            self.request.other['portal_status_message'] = message
        if kw:
            for k, v in kw.items():
                self.request.form[k] = v

        return success

    def setRedirect(self, provider_id, action_path, **kw):
        utool = getToolByName(self.context, 'portal_url')
        portal_url = utool()

        if provider_id == 'context':
            provider = self.context
        else:
            provider = getToolByName(self.context, provider_id)
        try:
            target = provider.getActionInfo(action_path)['url']
        except ValueError:
            target = portal_url

        message = self.request.other.get('portal_status_message', '')
        kw['portal_status_message'] = message
        for k, v in kw.items():
            if not v:
                del kw[k]

        query = kw and ( '?%s' % make_query(kw) ) or ''
        self.request.RESPONSE.redirect( '%s%s' % (target, query) )

        return True
