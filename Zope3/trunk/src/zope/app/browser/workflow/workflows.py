from zope.app.browser.services.registration import \
     NameComponentRegistryView, NameRegistryView
from zope.app.traversing import traverse, getParent, getName
from zope.component import getView

class WorkflowsRegistryView(NameComponentRegistryView):

    def _getItem(self, name, view, cfg):
        item_dict = NameRegistryView._getItem(self, name, view, cfg)
        if cfg is not None:
            ob = traverse(getParent(getParent(cfg)), cfg.componentPath)
            url = str(getView(ob, 'absolute_url', self.request))
        else:
            url = None
        item_dict['url'] = url
        return item_dict
