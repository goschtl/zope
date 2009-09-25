# -*- coding: utf-8 -*-
import martian


class wrapper(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateClass
