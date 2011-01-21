from mypkg.app import AppSample

def test_app_create():
    app = AppSample()
    assert app is not None
