# -*- coding: utf-8 -*-

from megrok import resource
from hurry.jquery import jquery


class AjaxLib(resource.Library):
    resource.name('ajaxlib')
    resource.path('libs')

InlineValidation = resource.ResourceInclusion(
    AjaxLib, 'validation.js', depends=[jquery])

