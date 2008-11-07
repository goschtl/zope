import zope.component
import zope.interface
import zope.schema
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.viewlet.interfaces import IViewletManager
from zope.session.interfaces import ISession

from zope.schema import vocabulary
from z3c.formui import layout
from z3c.formui.interfaces import ICSS as ICSSFormUI
from z3c.form import button, field, form, group, widget

from keas.googlemap.interfaces import IGeocodeQuery, IGeocode, ICenteredGeocodes
from keas.googlemap import geocode
from keas.googlemap.browser import interfaces, GoogleMap, Marker


class IJavaScript(IViewletManager):
    """JavaScript viewlet manager."""

class ICSS(ICSSFormUI):
    """CSS viewlet manager."""

SESSION_KEY = 'keas.googlemap.demo'

class SessionProperty(object):

    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def __get__(self, inst, klass):
        session = ISession(inst.request)[SESSION_KEY]
        return session.get(self.name, self.default)

    def __set__(self, inst, value):
        session = ISession(inst.request)[SESSION_KEY]
        session[self.name] = value


class GeocodeQueryForm(form.EditForm):
    label = u'Geocode Query'
    fields = field.Fields(IGeocodeQuery)
    prefix = 'geocode'

    success = False
    _query = SessionProperty('query')
    def getContent(self):
        if self._query is None:
            self._query = geocode.GeocodeQuery(u'1600 Pennsylvania Ave, Washington D.C.')
        return self._query

    @button.buttonAndHandler(u'Submit')
    def submit(self, action):
        self.handleApply(self, action)
        try:
            self.status = "Found %s" % IGeocode(self.getContent())
            self.success = True
        except ValueError, e:
            self.status = str(e)
            return


class MarkersForm(form.AddForm):
    form.extends(form.AddForm)
    label = u"Map Markers"

    template = ViewPageTemplateFile("markers.pt")

    ignoreContext = True
    fields = field.Fields(interfaces.IMarker).select('html', 'popupOnLoad')
    fields+= field.Fields(zope.schema.TextLine(
        title=u'Query',
        __name__='query',
        required=True))
    markers = SessionProperty('markers')

    def __init__(self, context, request):
        super(MarkersForm, self).__init__(context, request)
        if self.markers is None:
            self.markers = []

    def create(self, data):
        query = geocode.GeocodeQuery(data['query'])
        marker = Marker(geocode=IGeocode(query),
                        html=data['html'],
                        popupOnLoad=data['popupOnLoad'])
        return marker

    def add(self, obj):
        self.markers.append(obj)

    def nextURL(self):
        return '.'

    @button.buttonAndHandler(u'Clear Markers')
    def clear(self, action):
        self.markers = []


class DemoPage(layout.FormLayoutSupport, group.GroupForm, form.EditForm):
    form.extends(form.EditForm)
    label=u"Google Map Demo"

    template = ViewPageTemplateFile("demo.pt")

    fields = field.Fields(interfaces.IGoogleMap).select(
        'zoom','type','width','height','controls')

    googleMap = SessionProperty('googleMap')

    def __init__(self, context, request):
        super(DemoPage, self).__init__(context, request)
        if self.googleMap is None:
            self.googleMap = GoogleMap(markers=[Marker(geocode.Geocode(3.123,42.231))])
        self.geocodeForm = GeocodeQueryForm(context, request)
        self.markersForm = MarkersForm(context, request)

    def update(self):
        super(DemoPage, self).update()
        self.geocodeForm.update()
        self.markersForm.update()
        self.googleMap.markers = self.markersForm.markers
        self.googleMap.update()

    def getContent(self):
        return self.googleMap

    @button.buttonAndHandler(u'Revert to Defaults')
    def defaults(self, action):
        self.googleMap = GoogleMap(markers=[Marker(geocode.Geocode(3.123,42.231))])
