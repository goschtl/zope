from Products.Five import zcml

class FunctionalLayer:

    @classmethod
    def setUp(cls):
        zcml.load_site()

    @classmethod
    def tearDown(cls):
        raise NotImplementedError
