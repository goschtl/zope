import unittest

from ocql.ocqlengine import OCQLEngine

class ElementTest(unittest.TestCase):
    engine = OCQLEngine()

    def generic_test(self, query, result):
        print "Running query: `%s'"%query
        q = self.engine.compile(query)
        self.assertEqual(q.execute(), result)
    
    def generic_testl(self, query, result):
        print "Running query: `%s'"%query
        q = self.engine.compile(query)
        self.assertEqual(len(q.execute()), result)

    def test_set(self):
        self.generic_test("set [ | 1 ]", set([1]))
    
#    def test_bag(self):
#        self.generic_test("bag [ | 1 ]", bag([1]))

#    def test_list(self):
#        self.generic_test("list [ | 1 ]", [1])

    def test_union(self):
        self.generic_test("set [ | 1 ] union set [|2]", set([1, 2]))

    def test_differ(self):
        self.generic_test("set [ | 1 ] differ set [|2]", set([]))

    def test_in(self):
        self.generic_testl("set [ i in ICurses | i ]", 3)

    def test_count(self):
        self.generic_test("size set [ i in ICurses | i ]", 3)

def test_suite():
    tests=[]

    tests.append(unittest.makeSuite(ElementTest))

    return unittest.TestSuite(tests)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
    #engine = OCQLEngine()
    #query="set [|1]"
    #q = engine.compile(query)
    #print q.execute()

