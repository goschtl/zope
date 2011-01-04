from zope.pytest import argument

# test the argument decorator

def test_argument_decorator():

    @argument
    def myarg():
        return {'message': 'helloworld'}

    assert pytest_funcarg__myarg()['message'] == 'helloworld'


