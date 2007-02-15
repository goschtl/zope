import unittest
from zope.testing.doctest import DocTestSuite

def test_container():
    """
    Let's make a container and add a few items.  As you can see, we
    can use the regular IContainer API (Python's mapping API):

      >>> from megrok.five import Container, Model
      >>> folder = Container()
      >>> folder['garfield'] = Model('garfield')
      >>> folder['john'] = Model('john')
      >>> folder['odie'] = Model('odie')

    The rest of the mapping API is also supported:

      >>> sorted(folder)  # test __iter__
      ['garfield', 'john', 'odie']

      >>> sorted(folder.keys())
      ['garfield', 'john', 'odie']

      >>> sorted(model.getId() for model in folder.values())
      ['garfield', 'john', 'odie']

      >>> sorted((name, model.getId()) for name, model in folder.items()) # doctest: +NORMALIZE_WHITESPACE
      [('garfield', 'garfield'),
       ('john', 'john'),
       ('odie', 'odie')]

      >>> 'garfield' in folder  # test __contains__
      True

      >>> len(folder)  # test __len__
      3

      >>> folder.get('garfield') == folder['garfield']
      True
      >>> folder.get('not-there') is None
      True
      >>> folder.get('not-there', 'then take me')
      'then take me'

      >>> del folder['odie']  # test __delitem__
      >>> len(folder)
      2
      >>> sorted(folder)
      ['garfield', 'john']

    """

def test_suite():
    return unittest.TestSuite([
        DocTestSuite(),       
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
