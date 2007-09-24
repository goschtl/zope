# -*- coding: UTF-8 -*-

from testdb import TestMetadata

metadata = TestMetadata(None)

#reduce(set.union,
#    map(lambda c: reduce(set.union,
#        map(lambda d: (
#            (d.name=="Computing Science") and
#            (((d==set(filter(lambda i: i.runBy,c))) and
#                (((c.credits<=3) and (((1<=c.credits) and
#                    (set([c])) or (set()))) or (set()))) or
#                (set()))) or (set())),
#            set(metadata.getAll("IDepartments"))) ,
#        set()),set(metadata.getAll("ICurses"))) ,
#    set())


#map(lambda c: reduce(set.union,
#    map(lambda d: ((d.name=="Computing Science")),
#        set(metadata.getAll("IDepartments"))), set()),set(metadata.getAll("ICurses")))

#x = reduce(set.union,
#    map(lambda c: reduce(set.union,
#        map(lambda d: (
#            (d.name=="Computing Science")
#            and (d==set(filter(lambda i: i.runBy,c)))
#            and (set([c]))
#            or (set())) ,
#            set(metadata.getAll("IDepartments"))) ,
#        set()),set(metadata.getAll("ICurses"))) ,
#    set())

#x = reduce(set.union,
#    map(lambda c: reduce(set.union,
#        map(lambda d: (
#            (d.name=="Computing Science")
#            and (set([c]))
#            or (set())) ,
#            set(metadata.getAll("IDepartments"))) ,
#        set()),set(metadata.getAll("ICurses"))) ,
#    set())

x=reduce(set.union,
    map(lambda c: reduce(set.union,
        map(lambda d: (
            (d.name=="Computing Science") and
            (((d==set(filter(lambda i: i.runBy,[c]))) and
                (
                    (
                        (c.credits<=3)
                        and (
                                (
                                    (1<=c.credits)
                                    and
                                    (set([c]))
                                    or (set())
                                )
                            ) or (set())
                    )
                ) or
                (set()))) or (set())),
            set(metadata.getAll("IDepartments"))) ,
        set()),set(metadata.getAll("ICurses"))) ,
    set())


x = reduce(set.union,
    map(lambda c: reduce(set.union,
        map(lambda d: (
            (d.name=="Computing Science") and
            (((d==set(filter(lambda i: i.runBy,[c]))) and
                ((((
                    (set([c])) or (set()))) or (set()))) or
                (set()))) or (set())),
            set(metadata.getAll("IDepartments"))) ,
        set()),set(metadata.getAll("ICurses"))) ,
    set())


for i in x:
    print i.name