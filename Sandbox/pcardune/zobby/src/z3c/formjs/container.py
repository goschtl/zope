from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.location.location import LocationProxy
from zif.jsonserver.jsonrpc import MethodPublisher


class ContainerHandler(MethodPublisher):
    """simple json-rpc view class for doing things with containers."""

    def getAttributes(self, attributes):
        result = []
        for key, value in self.context.items():
            data = [key,{}]
            for attribute in attributes:
                data[1][attribute] = getattr(value, attribute)
            result.append(data)
        return result

