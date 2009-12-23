# -*- coding: utf-8 -*-
import martian


class formview(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateClass
