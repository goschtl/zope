from zope.traversing import api
from zope.dublincore.interfaces import IZopeDublinCore
from zope.traversing.browser import absoluteURL

from zc.table import column

class CheckboxColumn(column.Column):

    def renderCell(self, item, formatter):
        widget = (u'<input type="checkbox" '
                  u'name="selected:list" value="%s">')
        return widget %api.getName(item)


def getCreatedDate(item, formatter):
    formatter = formatter.request.locale.dates.getFormatter('date', 'short')
    return formatter.format(IZopeDublinCore(item).created)


def getModifiedDate(item, formatter):
    formatter = formatter.request.locale.dates.getFormatter('date', 'short')
    return formatter.format(IZopeDublinCore(item).modified)


def link(view='index', title=''):
    def anchor(value, item, formatter):
        url = absoluteURL(item, formatter.request) + '/' + view
        return u'<a href="%s" title="%s">%s</a>' %(url, title, value)
    return anchor

