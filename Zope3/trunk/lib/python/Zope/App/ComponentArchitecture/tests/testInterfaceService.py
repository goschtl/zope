from Interface import Interface
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp
from Zope.App.ComponentArchitecture.IGlobalInterfaceService \
     import IGlobalInterfaceService
from Zope.App.ComponentArchitecture.InterfaceService import InterfaceService
from Zope.App.ComponentArchitecture.IInterfaceService import IInterfaceService
from Interface.Verify import verifyObject
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.ComponentArchitecture.GlobalServiceManager \
     import serviceManager, defineService


class I(Interface):
    """bah blah
    """
    
class I2(Interface):
    """eek
    """
    
class I3(Interface):
    """
    """
    def one():
        """method one"""

    def two():
        """method two"""
        
class Test(CleanUp, TestCase):
    """Test Interface for InterfaceService Instance.
    """
    
    def testInterfaceVerification(self):
        
        verifyObject(IGlobalInterfaceService, InterfaceService())

    def testInterfaceService(self):
        service = InterfaceService()
        
        self.assertRaises(ComponentLookupError,
                          service.getInterface, 'Foo.Bar')
        self.assertEqual(service.queryInterface('Foo.Bar'), None)
        self.assertEqual(service.queryInterface('Foo.Bar', 42), 42)
        self.failIf(service.searchInterface(''))

        service.provideInterface('Foo.Bar', I)

        self.assertEqual(service.getInterface('Foo.Bar'), I)
        self.assertEqual(service.queryInterface('Foo.Bar'), I)
        self.assertEqual(list(service.searchInterface('')), [I])

        service.provideInterface('Foo.Baz', I2)

        result = list(service.searchInterface(''))
        result.sort()
        self.assertEqual(result, [I, I2])

        self.assertEqual(list(service.searchInterface('I2')), [I2])
        self.assertEqual(list(service.searchInterface('eek')), [I2])

        self.assertEqual(list(service.searchInterfaceIds('I2')), ['Foo.Baz'])
        self.assertEqual(list(service.searchInterfaceIds('eek')), ['Foo.Baz'])

        service.provideInterface('Foo.Bus', I3)
        self.assertEqual(list(service.searchInterface('two')), [I3])

def test_suite():
    return TestSuite((makeSuite(Test),))

if __name__=='__main__':
    main(defaultTest='test_suite')
    self.assertEqual(list(service.searchInterface('two')), [I3])
                

def test_suite():
    return TestSuite((makeSuite(Test),))

if __name__=='__main__':
    main(defaultTest='test_suite')

