try:
    __import__('pkg.resources').declare_namespace(__name__)
except ImportError:
    pass