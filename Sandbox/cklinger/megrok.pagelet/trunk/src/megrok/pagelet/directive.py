import martian

class template(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u'megrok.pagelet.template'
    
