import logging

from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse
import ZPublisher

from z3c.taskqueue.processor import BaseSimpleProcessor
from z3c.taskqueue.processor import BaseMultiProcessor
from z3c.taskqueue.processor import ERROR_MARKER

log = logging.getLogger('z3c.taskqueue')


class Response(HTTPResponse):
    """override setBody to avoid that method result gets turned to a string."""

    def setBody(self, body):
        self.body = body


class Z2PublisherMixin(object):

    def call(self, method, args=(), errorValue=ERROR_MARKER):
        path = self.servicePath[:] + [method]
        response = Response()
        env = {'SERVER_NAME': 'dummy',
                'SERVER_PORT': '8080',
                'PATH_INFO': '/' + '/'.join(path)}
        request = HTTPRequest(None, env, response)
        request.args = args
        conn = self.db.open()
        root = conn.root()
        request['PARENTS'] = [root['Application']]
        try:
            try:
                ZPublisher.Publish.publish(request, 'Zope2', [None])
            except Exception, error:
                # This thread should never crash, thus a blank except
                log.error('Processor: ``%s()`` caused an error!' % method)
                log.exception(error)
                return errorValue is ERROR_MARKER and error or errorValue
        finally:
            request.close()
            conn.close()
            return request.response.body


class SimpleProcessor(Z2PublisherMixin, BaseSimpleProcessor):
    """ SimpleProcessor for Zope2 """


class MultiProcessor(Z2PublisherMixin, BaseMultiProcessor):
    """ SimpleProcessor for Zope2 """
