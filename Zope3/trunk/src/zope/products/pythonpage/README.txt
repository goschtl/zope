Python Page
===========

Python Page provides the user with a content object that interprets Python in
content space. To save typing and useless messing with output, any
free-standing string and print statement are considered for output; see the
example below.


Installation
------------

  1. In your 'products.zcml' file make sure that  you register this product 
     using::

       <include package="zope.products.pythonpage"/>

  2. Restart Zope 3.

  3. You can now create a new content type called "Python Page". Try the
     following source::

       '''
       <html>
         <body>
           <ul>
       '''
       
       import time
       print time.asctime()
       
       '''
           </ul>
         </body>
       </html>
       '''



