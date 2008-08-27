# -*- coding: UTF-8 -*-

"""Main

$Id: engine.py 89787 2008-08-13 08:26:04Z adamg $
"""

from zope.component import provideAdapter

from ocql.testing import utils
from ocql.testing.database import TestMetadata
from ocql.engine import OCQLEngine

def console():
    utils.setupAdapters(None)
    provideAdapter(TestMetadata)

    engine = OCQLEngine()

    while True:
        inp = raw_input("ocql>")

        if inp == "bye" or inp == "quit":
            break

        try:
            print engine.compile(inp).execute()
        except Exception, e:
            print "Exception occurred: %s" % str(e)