This package provides a trused layer setup for Zope3. Truted means you can 
travers over objects which you don't have permission for. This is needed if you
have a setup with more then one IAuthentication utility. Otherwise you don't
hav a chance to traverse to the IAthentication utility in the subsite without
to authenticate at the parent IAuthentication.
