from zope import interface
from zope import component

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.contentprovider.interfaces import IContentProvider

from z3c.resourceinclude.interfaces import IResourceCollector
from chameleon.zpt.template import PageTemplateFile

import os.path

import mimetypes
if not '.kss' in mimetypes.types_map:
    mimetypes.add_type('text/kss', '.kss')


def guess_mimetype(resource):
    return resource.context.content_type


def local_file(filename):
    return os.path.join(os.path.dirname(__file__), filename)


class ResourceIncludeProvider(object):
    interface.implements(IContentProvider)
    component.adapts(interface.Interface, IBrowserRequest, IBrowserView)

    template = PageTemplateFile(local_file("provider.pt"))

    def __init__(self, context, request, view):
        self.context = context
        self.request = request
        self.__parent__ = view

    def update(self):
        self.collector = IResourceCollector(self.request)

    def render(self):
        resources = [{'content_type': guess_mimetype(resource),
                      'url': resource()} for \
                     resource in self.collector.collect()]

        return self.template(resources=resources)
