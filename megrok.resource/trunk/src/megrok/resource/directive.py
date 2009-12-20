# -*- coding: utf-8 -*-

import martian
from hurry.resource.interfaces import IInclusion


def validateInclusion(directive, value):
    if not IInclusion.providedBy(value):
        raise ValueError(
            "You can only include IInclusions components.")


class use_hash(martian.Directive):
    scope = martian.CLASS_OR_MODULE
    store = martian.ONCE
    default = True

    def factory(self, value):
        return bool(value)


class include(martian.Directive):
    scope = martian.CLASS
    store = martian.MULTIPLE
    validate = validateInclusion
