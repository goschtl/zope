import grok
from zope.component import queryMultiAdapter
from z3c.template.interfaces import ILayoutTemplate
from zope.publisher.publish import mapply


class Layout(object):
    """ A basic class for Layouts"""
    pass


class Pagelet(grok.View):
    """This is the BaseClass for view Pagelets
    """
    grok.baseclass()
    layout = None

    def render(self):
        return self._render_template()

    render.base_method = True

    def __call__(self):
        """Calls update and returns the layout template which calls render."""
        self.update()
        if self.layout is None:
            layout = queryMultiAdapter(
                (self.context, self.request), ILayoutTemplate)
            if layout is None:
                raise NotImplementedError(
                    """Impossible to find a suitable layout for %r.
                    This is an unimplemented siutation. Please, provide
                    a useable layout or check your components.""" % self
                    )
            return layout(self)
        return self.layout()


class FormPageletMixin(object):
    """This is the BaseClass for form Pagelets
    """
    layout = None

    def __call__(self):
        """Calls update and returns the layout template which calls render.
        """
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            return

        self.update_form()
        if self.layout is None:
            layout = queryMultiAdapter(
                (self.context, self.request), ILayoutTemplate)
            if layout is None:
                raise NotImplementedError(
                    """Impossible to find a suitable layout for %r.
                    This is an unimplemented siutation. Please, provide
                    a useable layout or check your components.""" % self
                    )
            return layout(self)
        return self.layout()
