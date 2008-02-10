from zc.selenium.pytest import Test

class WebSiteTestSuite(Test):

    def setUp(self):
        super(WebSiteTestSuite, self).setUp()
        print self.selenium.server
        self.baseURL = 'http://%s/' % self.selenium.server

    def reset(self):
        s = self.selenium
        s.open(self.baseURL)

    def sharedSetUp(self):
        super(WebSiteTestSuite, self).sharedSetUp()

    def sharedTearDown(self):
        super(WebSiteTestSuite, self).sharedTearDown()

    def open(self, path):
        self.selenium.open(self.baseURL + path)

    def test_base(self):
        s = self.selenium
        self.reset()
        s.verifyTextPresent('Remoteinclude Demo')

