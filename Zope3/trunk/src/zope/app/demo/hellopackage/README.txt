A Zope 3 "Hello World" example. We create a content object that has
a method called 'getHello' that will return Hello world. We make
a very basic view for this content object. Finally we make the object
addable.

In this package we are excessively explicit in the naming in an attempt to
make it more clear what's going on, especially in the ZCML. Instead of naming
everything left and right 'Hello', there is now a distinction in the package
name, module name, etc. This is not the normal style of naming in Zope 3
however.

'configure.zcml' contains a lot of comments.

To enable this, go to your 'products.zcml' in the Zope 3 root and 
add the line:

<include package="zope.app.demo.hellopackage" />

presuming you installed this package in ZopeProducts.