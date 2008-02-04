from Products.CMFCore.permissions import setDefaultRoles

AddFeature = "zopeorg.theme: Add Feature"

setDefaultRoles(AddFeature, ("Manager", "Owner"))
