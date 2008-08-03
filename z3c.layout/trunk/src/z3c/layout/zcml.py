from zope.component import zcml
from zope.app.publisher.browser import resourcemeta

import interfaces
import model
import utils
import md5
import os

class LayoutDirective(object):
    def __init__(self, _context, name, template, regions=()):
        self._context = _context
        self.name = name
        self.template = template
        self.regions = set()

    def region(self, _context, *args, **kwargs):
        self.regions.add(
            model.Region(*args, **kwargs))

    def __call__(self):
        path, filename = os.path.split(self.template)

        # compute resource directory name
        dotted_name = utils.dotted_name(path)
        resource_name = md5.new(dotted_name).hexdigest()
        resource_path = '++resource++%s' % resource_name
        
        layout = model.Layout(
            self.name, self.template, resource_path, self.regions)

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
