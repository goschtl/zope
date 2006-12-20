from distutils.core import setup
import py2app

plist = dict(
    CFBundleName = "Zem",
    CFBundleIdentifier = "com.urbanape.zopeeditmanager",
    CFBundleShortVersionString = "Version 0.9.8",
    CFBundleGetInfoString = ("Zem version 0.9.8, "
                             "Copyright 2003-2006 Zope Corporation"),
    NSHumanReadableCopyright = "Copyright 2003-2006 Zope Corporation",
    CFBundleIconFile = "ZEM.icns",
    CFBundleInfoDictionaryVersion = "6.0",
    CFBundlePackageType = "APPL",
    CFBundleSignature = "ZEDM",
    CFBundleVersion = "0.9.8",
    NSMainNibFile = "MainMenu",
    NSPrincipalClass = "NSApplication",
    CFBundleDevelopmentRegion = "English",
    CFBundleDocumentTypes = [
        dict(CFBundleTypeExtensions = ["zem"],
             CFBundleTypeOSTypes = ["ZEMD"],
             CFBundleTypeMIMETypes = ["application/x-zope-edit"],
             CFBundleTypeRole = "Viewer",
             CFBundleTypeIconFile = "ZEMDocument.icns")])

setup(
    data_files = ["Nibs/MainMenu.nib",
                  "Nibs/Preferences.nib",
                  "Resources/Files.png",
                  "Resources/HelperApps.png",
                  "Resources/WebDAV.png",
                  "Resources/ZEM.icns",
                  "Resources/ZEMDocument.icns",
                  "Resources/add_disabled.png",
                  "Resources/add_idle.png",
                  "Resources/add_pressed.png",
                  "Resources/remove_disabled.png",
                  "Resources/remove_idle.png",
                  "Resources/remove_pressed.png",
                  "Resources/com.urbanape.zopeeditmanager.plist"
                  ],
    app = [dict(
        script="ZemAppDelegate.py", plist=plist),
           ],
    )
