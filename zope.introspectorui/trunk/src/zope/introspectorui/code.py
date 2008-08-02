import grokcore.view as grok

from zope.location.location import located

from zope.introspector.code import PackageInfo

class Package(grok.View):
    grok.context(PackageInfo)
    grok.name('index')

    def update(self):
        self.files = self.getTextFileUrls()
        self.zcmlfiles = self.getZCMLFileUrls()
        self.subpks = self.getSubPackageUrls()
        self.modules = self.getModuleUrls()

    def _getFileUrls(self, filenames):
        result = []
        package = self.context.context
        for name in filenames:
            try:
                file = located(package[name], package, name)
                result.append(dict(name=name, url=self.url(file)))
            except:
                print "PROBLEM: ", name
        return sorted(result)

    def getTextFileUrls(self):
        filenames = self.context.getPackageFiles()
        return self._getFileUrls(filenames)

    def getZCMLFileUrls(self):
        try:
            filenames = self.context.getZCMLFiles()
        except:
            print "PROBLEM."
        return self._getFileUrls(filenames)

    def _getItemUrls(self, mod_infos):
        result = []
        package = self.context.context
        for info in mod_infos:
            mod = located(package[info.name], package, info.name)
            result.append(dict(name=info.name, url=self.url(mod)))
        return result
        
    def getSubPackageUrls(self):
        mod_infos = self.context.getSubPackages()
        return sorted(self._getItemUrls(mod_infos))

    def getModuleUrls(self):
        mod_infos = self.context.getModules()
        return sorted(self._getItemUrls(mod_infos))
