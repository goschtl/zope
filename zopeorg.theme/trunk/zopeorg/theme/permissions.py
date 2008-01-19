from Products.CMFCore.permissions import setDefaultRoles

AddFeature = "zopeorg.theme: Add Bla"

setDefaultRoles(AddFeature, ("Manager", "Owner"))
