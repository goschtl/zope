# -*- coding: utf-8 -*-
import os

import zope.component
import grokcore.view
import grokcore.formlib
import grokcore.component as grok
from zope.interface import Interface
from zope.publisher.publish import mapply
from megrok.layout.interfaces import IPage, ILayout


class Layout(object):
    """A layout object.
    """
    grok.baseclass()
    grok.implements(ILayout)

    def __init__(self, request, context):
        self.context = context
        self.request = request
        self.view = None

        if getattr(self, 'module_info', None) is not None:
            self.static = zope.component.queryAdapter(
                self.request, Interface,
                name=self.module_info.package_dotted_name
                )
        else:
            self.static = None

    def default_namespace(self):
        namespace = {}
        namespace['view'] = self.view
        namespace['layout'] = self
        namespace['static'] = self.static
        namespace['context'] = self.context
        namespace['request'] = self.request
        return namespace

    def namespace(self):
        return {}

    def update(self):
        pass

    @property
    def response(self):
        return self.request.response

    def _render_template(self):
        return self.template.render(self)

    def render(self):
        return self._render_template()

    render.base_method = True

    def __call__(self, view):
        self.view = view
        self.update()
        return self.render()


class Page(grokcore.view.View):
    """A view class.
    """
    grok.baseclass()
    grok.implements(IPage)

    def __init__(self, context, request):
        super(Page, self).__init__(context, request)
        self.layout = None

    def __call__(self):
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return
        self.layout = zope.component.getMultiAdapter(
            (self.request, self.context), ILayout)
        return self.layout(self)

    def default_namespace(self):
        namespace = super(Page, self).default_namespace()
        namespace['layout'] = self.layout
        return namespace

    def content(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)


class LayoutAwareForm(object):
    """A mixin to make form aware of layouts.
    """

    def __init__(self, context, request):
        super(LayoutAwareForm, self).__init__(context, request)
        self.layout = None

    def default_namespace(self):
        namespace = super(LayoutAwareForm, self).default_namespace()
        namespace['layout'] = self.layout
        return namespace

    def content(self):
        template = getattr(self, 'template', None)
        if template is not None:
            return self._render_template()
        return mapply(self.render, (), self.request)

    def __call__(self):
        """Calls update and returns the layout template which calls render.
        """
        mapply(self.update, (), self.request)
        if self.request.response.getStatus() in (302, 303):
            # A redirect was triggered somewhere in update().  Don't
            # continue rendering the template or doing anything else.
            return

        self.update_form()
        if self.request.response.getStatus() in (302, 303):
            return

        self.layout = zope.component.getMultiAdapter(
            (self.request, self.context), ILayout)
        return self.layout(self)


# Default forms for form without the html and body tags
default_form_template = grokcore.view.PageTemplateFile(os.path.join(
    'templates', 'default_edit_form.pt'))
default_form_template.__grok_name__ = 'default_edit_form'
default_display_template = grokcore.view.PageTemplateFile(os.path.join(
    'templates', 'default_display_form.pt'))
default_display_template.__grok_name__ = 'default_display_form'


class Form(LayoutAwareForm, grokcore.formlib.Form):

    grok.baseclass()
    template = default_form_template


class AddForm(LayoutAwareForm, grokcore.formlib.AddForm):

    grok.baseclass()
    template = default_form_template


class EditForm(LayoutAwareForm, grokcore.formlib.EditForm):

    grok.baseclass()
    template = default_form_template


class DisplayForm(LayoutAwareForm, grokcore.formlib.DisplayForm):

    grok.baseclass()
    template = default_display_template
