from Products.Five import BrowserView

class TestView(BrowserView):
    def test(self):
        return "hoi"

