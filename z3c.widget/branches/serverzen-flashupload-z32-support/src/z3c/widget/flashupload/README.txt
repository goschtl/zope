===================
FLASH UPLOAD WIDGET
===================

Requirements
============

  * Zope 3.2+

Flash Upload Vars Page
======================

The flashupload vars page configures the flash frontend.

    >>> from z3c.widget.flashupload import upload
    >>> from zope.testing.doctestunit import DocTestSuite
    >>> from zope.publisher.browser import TestRequest
    >>> from zope.app.pagetemplate import ViewPageTemplateFile
    >>> from zope.app.pagetemplate.simpleviewclass import SimpleViewClass
    >>> request = TestRequest()
    >>> context = object()
    >>> viewClass = SimpleViewClass('flashuploadvars.pt', bases=(upload.FlashUploadVars,))
    >>> view = viewClass(context, request)
    >>> print view()
    <?xml version="1.0" ?>
    <var>
        <var name="file_progress">File Progress</var>
        <var name="overall_progress">Overall Progress</var>
        <var name="error">Error on uploading files</var>
        <var name="uploadcomplete">all files uploaded</var>
    </var>
    >>> view.allowedFileTypes = ('.jpg', '.gif')
    >>> print view()
    <?xml version="1.0" ?>
    <var>
    ...
        <var name="allowedFileType">.jpg</var>
        <var name="allowedFileType">.gif</var>
     </var>
    
