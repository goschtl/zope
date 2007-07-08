import zope.interface

class IMarsAdapterDirectives(zope.interface.Interface):

    def factory(factory):
        """The factory to be registered as an adapter"""
        pass

