import grokcore.view as grok

from zope.location.location import located

from zope.introspector.code import PackageInfo

class Package(grok.View):
    grok.context(PackageInfo)
    grok.name('index')

    def update(self):
        self.files = self.getTextFileUrls()

    def getTextFileUrls(self):
        filenames = self.context.getPackageFiles()
        result = []
        package = self.context.context
        for name in filenames:
            file = located(package[name], package, name)
            result.append(dict(name=name, url=self.url(file)))
        return result
