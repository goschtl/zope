from mypkg.app import AppSample

def test_app_create():
    # Assure we can create instances of `AppSample`
    app = AppSample()
    assert app is not None
