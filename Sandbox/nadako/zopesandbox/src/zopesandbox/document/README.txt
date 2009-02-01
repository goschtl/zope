=========
Documents
=========

This package provides a simple implementation of document content
type. Documents have title, short description and body text. The
latter one can contain HTML tags to be rendered as is.

   >>> from zopesandbox.document.interfaces import IDocument
   >>> from zopesandbox.document.document import Document
   >>> from zope.interface.verify import verifyObject
   
   >>> doc = Document()
   >>> verifyObject(IDocument, doc)
   True

   >>> doc.title = u'Main page'
   >>> doc.description = u'This is the front page of our website'
   >>> doc.body = u'<h2>Welcome</h2><p>You are visiting http://foo.com/</p>'

Also, the document's title and description are its Dublin Core unqualified
title and description at the same time.

   >>> from zope.dublincore.interfaces import IDCDescriptiveProperties
   >>> dc = IDCDescriptiveProperties(doc)
   >>> dc.title
   u'Main page'
   >>> dc.description
   u'This is the front page of our website'
