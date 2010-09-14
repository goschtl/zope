# -*- coding: utf-8 -*-

import grokcore.view
from zope.interface import alsoProvides
from zope.publisher.publish import mapply
from grok.interfaces import IGrokSecurityView
from zope.security.proxy import removeSecurityProxy



class ViewExtension(grokcore.view.View):

    def __init__(self, context, request):
        self.view = context
        super(grokcore.view.View, self).__init__(context, request)
        if not IGrokSecurityView.providedBy(context):
            self.view = removeSecurityProxy(self.view)
            alsoProvides(self.view, IGrokSecurityView)
        if not IGrokSecurityView.providedBy(self.view.context):
            self.context = removeSecurityProxy(self.view.context)
            alsoProvides(self.context, IGrokSecurityView)

    def __call__(self):
        view_name = self.__view_name__
        method = getattr(self, view_name)
        method_result = mapply(method, (), self.request)
        return method_result 

    def render(self):
        return "BLA"


def jsonify(method):
    def wrapper(self, *args, **kwargs):
        import simplejson
        data = method(self, *args, **kwargs)
        return simplejson.dumps(data) 
    return wrapper
