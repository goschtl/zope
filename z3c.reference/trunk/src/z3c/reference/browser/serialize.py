import urllib

from BeautifulSoup import BeautifulSoup

from zope.formlib import form
from zope.publisher.browser import TestRequest

from views import getEditorView, getOpenerView


def serializeForm(html):
    res = []
    for tag in BeautifulSoup(html)(['input', 'textarea']):
        name = tag.get('name', None)
        t = tag.get('type', 'text')
        value = tag.get('value', None)
        if value is None:
            value = tag.renderContents(encoding=None)
        if (   t not in ('hidden', 'text')
            or None in (name, value)
           ):
            continue
        res.append((name, value.encode('utf-8')))
    return urllib.urlencode(res)


def serializeRelation(ref, request, settingName):
    klass = getEditorView(ref.target, request, settingName).__class__
    r = TestRequest()
    view = klass(ref, r)
    view = ApplyForm(ref, r, view.form_fields)
    view.update()
    html = ''
    for widget in view.widgets:
        v = widget()
        html += v
    return serializeForm(html)


class ApplyForm(form.EditForm):

    def __init__(self, context, request, form_fields):
        self.form_fields = form_fields
        super(ApplyForm, self).__init__(context, request)

