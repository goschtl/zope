import martian

class layout(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u'megrok.pagelet.layout'

class template(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u'megrok.pagelet.template'
