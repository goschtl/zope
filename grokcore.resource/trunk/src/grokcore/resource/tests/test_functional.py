import unittest
from grokcore.resource.testing import browser_layer

class Functional(unittest.TestCase):
    layer = browser_layer

    def test_add_resource_includer_interface(self):
        '''As a result of being grokked, the View class
        gains an interface declaration.'''
        from grokcore.resource.tests.fixtures import MyView
        from grokcore.resource.interfaces import IResourcesIncluder
        self.assertTrue(IResourcesIncluder.implementedBy(MyView))

        # This doesn't happen for all views:
        from grokcore.resource.tests.fixtures import MySuperView
        self.assertFalse(IResourcesIncluder.implementedBy(MySuperView))

        # Adding the interface, does not affect the existing
        # interface implementations:
        from grokcore.resource.tests.fixtures import MySuperViewWithResource
        self.assertTrue(
            IResourcesIncluder.implementedBy(MySuperViewWithResource))
        from grokcore.resource.tests.fixtures import IMySuperIface
        self.assertTrue(IMySuperIface.implementedBy(MySuperViewWithResource))

    def test_render_fanstatic_urls(self):
        from zope.app.wsgi.testlayer import Browser
        browser = Browser('http://localhost/@@myview')
        self.assertEqual('''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/a.css" />

</head>
<body>
</body>
</html>
''', browser.contents)

    def test_resource_need_in_update(self):
        '''We can both need the resources in the View definition
        and in the update method of the view.'''
        from zope.app.wsgi.testlayer import Browser
        browser = Browser('http://localhost/@@viewwithresourceinupdate')
        self.assertEqual('''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/a.css" />
<link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/d.css" />

</head>
<body>
</body>
</html>
''', browser.contents)

    def test_multiple_resources(self):
        '''The `include` directive accepts multiple resources.'''
        from zope.app.wsgi.testlayer import Browser
        browser = Browser('http://localhost/@@viewwithmultipleresources')
        self.assertEqual('''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/b.css" />
<link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/c.css" />

</head>
<body>
</body>
</html>
''', browser.contents)

    def test_multiple_resource_calls(self):
        '''The `include` directive can be called multiple times.'''
        from zope.app.wsgi.testlayer import Browser
        browser = Browser('http://localhost/@@viewwithmultipleresourcecalls')
        self.assertEqual('''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/a.css" />
<link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/b.css" />
<link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/c.css" />

</head>
<body>
</body>
</html>
''', browser.contents)

    def test_resources_override_in_subclass(self):
        '''The `include` directive overrides resources needed in super classes.'''
        from zope.app.wsgi.testlayer import Browser
        browser = Browser('http://localhost/@@viewwithownresource')
        self.assertEqual('''\
<html>
<head>
    <link rel="stylesheet" type="text/css" href="http://localhost/fanstatic/grokcore.resource.tests/b.css" />

</head>
<body>
</body>
</html>
''', browser.contents)

    def test_validation(self):
        '''The `include` directive will raise an error if the provided
        value is not a valid inclusion object.'''
        import grokcore.resource
        sneaky = object()

        try:
            class Sneaky(object):
                grokcore.resource.include(object())
        except ValueError as err:
            pass
        self.assertEqual('You can only include fanstatic Dependable '
            '(Resource or Group) components.', str(err))

# XXX Test clearing of needed resources in case of error.
