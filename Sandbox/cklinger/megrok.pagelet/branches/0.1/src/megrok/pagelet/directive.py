import martian


class template(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    validate = martian.validateText
    default = u'megrok.pagelet.template'
