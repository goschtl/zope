# XXX awful hack to make sure we don't get a warning due to two
# namespace packages being loaded. Why this is needed I do not know,
# haven't seen this before :(
import warnings
warnings.filterwarnings("ignore", "Module (.*) was already imported (.*)")

# this is a namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)
