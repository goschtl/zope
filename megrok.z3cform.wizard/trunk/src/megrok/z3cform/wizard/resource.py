# -*- coding: utf-8 -*-

from megrok import resource
from hurry.jquery import jquery


class z3cWizardLib(resource.Library):
    resource.name('ajaxwizard')
    resource.path('wizard')

z3cWizard = resource.ResourceInclusion(
    z3cWizardLib, 'z3c.js', depends=[jquery])

