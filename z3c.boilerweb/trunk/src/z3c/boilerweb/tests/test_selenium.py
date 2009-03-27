import zc.selenium.pytest
class Test(zc.selenium.pytest.Test):
    """Basic tests.
    """

    def test_basic(self):
        s = self.selenium
        s.open('/index.html')
        s.clickAndWait('link=start building!')
        s.type('form-widgets-name','test')
        s.clickAndWait('form-buttons-apply')
        s.clickAndWait('link=Boil It!')

