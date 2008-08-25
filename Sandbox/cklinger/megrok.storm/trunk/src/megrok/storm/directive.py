import martian

class storename(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u'megrok.storm.store'

class uri(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE

class tablename(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u''

class key(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u''

class rdb_object(martian.Directive):
    scope = martian.CLASS
    store = martian.ONCE
    default = u''
