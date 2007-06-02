from paste.evalexception.middleware import EvalException

class ZopeEvalException(EvalException):

    def __call__(self, environ, start_response):
        environ['wsgi.handleErrors'] = False
        return super(ZopeEvalException, self).__call__(environ, start_response)

def zope_eval_exception(app, global_conf):
    return ZopeEvalException(app)
