# http://docs.python.org/lib/module-pkgutil.html
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
