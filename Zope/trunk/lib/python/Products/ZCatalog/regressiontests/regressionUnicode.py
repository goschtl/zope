import os,sys
execfile(os.path.join(sys.path[0],'framework.py'))
import unittest

import Zope
from Products.ZCatalog.ZCatalog import ZCatalog


from Products.PluginIndexes.TextIndex import Splitter

# This patch pretends the ZCatalog is using the Unicode Splitter
# but by default the ZCatalog/TextIndexes uses the standard
# non-unicode-aware ZopeSplitter

Splitter.availableSplitters =    [ ("UnicodeSplitter" , "Unicode-aware splitter")]
Splitter.splitterNames =    [ "UnicodeSplitter" ]



class TO:

    def __init__(self,txt,kw=''):
        self.text = txt
        self.kw   = kw


class UnicodeTextIndexCatalogTest(unittest.TestCase):

    def setUp(self):

        self.cat = ZCatalog("catalog")
        self.cat.addIndex('text',"TextIndex")
        self.cat.addColumn('text')
        self.cat.addIndex('kw','KeywordIndex')
        self.cat.addColumn('kw')

        t1 = TO('the quick brown fox jumps over the lazy dog',['quick','fox'])
        t2 = TO('i am the nice alien from the future',['alien','future'])
        t3 = TO('i am a brown fox dancing with a future alien',['zerst�rt','k�nnten'])
        t4 = TO('i am a brown ' + unicode('fox') + ' dancing with a future alien',[])
        t5 = TO("""
        Die USA und Gro�britannien k�nnen nach der Zerst�rung der
        afghanischen Luftabwehr nun rund um die Uhr Angriffe fliegen. Das gab 
        Verteidigungsminister Donald Rumsfeld bekannt. Bei den dreit�gigen Angriffen
        seien auch bis auf einen alle Flugpl�tze der Taliban zerst�rt worden. Rumsfeld
        erkl�rte weiter, er k�nne die Berichte nicht best�tigen, wonach bei den 
        amerikanischen Angriffen vier afghanische Mitarbeiter einer von den UN
        finanzierten Hilfsorganisation get�tet wurden. Diese k�nnten auch durch
        Gegenfeuer der Taliban get�tet worden sein.
        """,[unicode('dreit�gigen','latin1')])
                                                                                                            

        self.cat.catalog_object(t1,"o1")
        self.cat.catalog_object(t2,"o2")
        self.cat.catalog_object(t3,"o3")
        self.cat.catalog_object(t4,"o4")
        self.cat.catalog_object(t5,"o5")

        self.tests = [('quick',('o1',)),
              ('fox',('o1','o2','o3','o4')),
              ('afghanischen', ('o5',)),
              ('dreit�gigen',('o5',))
            ]

        
        self.kw_tests = [ ('quick',('o1',) ),
                          ('zerst�rt',('o3',)),
                          ('dreit�gigen',('o5',))
                        ]


    def testAsciiQuery(self):
        """ simple query test """

        for q,objs in self.tests:
            res=self.cat.searchResults({'text':{'query':q}})

            for r in res:
                assert r.getURL() in objs,\
                    "%s: %s vs %s" % (q,str(r.getURL()),str(objs)) 


    def testUnicodeQuery(self):
        """ unicode query test """

        for q,objs in self.tests:
            res=self.cat.searchResults({'text':{'query':unicode(q,'latin1')}})

            for r in res:
                assert r.getURL() in objs, \
                    "%s: %s vs %s" % (q,str(r.getURL()),str(objs)) 


    def testAsciiKeywords(self):
        """ test keyword index """

        for q,objs in self.kw_tests:
            res=self.cat.searchResults({'kw':{'query':q}})

            for r in res:
                assert r.getURL() in objs, \
                    "%s: %s vs %s" % (q,str(r.getURL()),str(objs)) 


    def testUnicodeKeywords(self):
        """ test unicode keyword index """

        for q,objs in self.kw_tests:
            res=self.cat.searchResults({'kw':{'query':unicode(q,'latin1')}})

            for r in res:
                assert r.getURL() in objs, \
                    "%s: %s vs %s" % (q,str(r.getURL()),str(objs)) 


framework()

