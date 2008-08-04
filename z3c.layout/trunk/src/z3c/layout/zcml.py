from zope import interface
from zope import schema

from zope.component import zcml
from zope.configuration import fields
from zope.app.publisher.browser import resourcemeta

import interfaces
import model
import utils
import md5
import os

class ILayoutDirective(interface.Interface):
    name = interfaces.ILayout.get('name')
    template = interfaces.ILayout.get('template')
    
class IRegionDirective(interfaces.IRegion):
    pass

class ITransformDirective(interface.Interface):
    handler = fields.GlobalObject(
        title=u"Handler that implements transform",
        required=True)

    xpath = schema.TextLine(
        title=u"X-path expression for transform",
        required=False)

class LayoutDirective(object):
    def __init__(self, _context, name, template):
        self._context = _context
        self.name = name
        self.template = template
        self.regions = set()
        self.transforms = set()
        
    def region(self, _context, *args, **kwargs):
        self.regions.add(
            model.Region(*args, **kwargs))

    def transform(self, _context, *args, **kwargs):
        self.transforms.add(
            model.Transform(*args, **kwargs))
                  
    def __call__(self):
        path, filename = os.path.split(self.template)

        # compute resource directory name
        dotted_name = utils.dotted_name(path)
        resource_name = md5.new(dotted_name).hexdigest()
        resource_path = '++resource++%s' % resource_name
        
        layout = model.Layout(
            self.name, self.template, resource_path,
            self.regions, self.transforms)

        # register resource directory
        resourcemeta.resourceDirectory(
            self._context,
            resource_name,
            path)

        # register layout
        zcml.utility(
            self._context,
            provides=interfaces.ILayout,
            component=layout,
            name=self.name)
