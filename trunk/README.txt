Zope External Editor

  The Zope External Editor is a new way to integrate Zope more seamlessly with
  client-side tools. It has the following features:
    
  - Edit objects locally, directly from the ZMI.
  
  - Works with any graphical editor application that can open a file from the 
    command line, including: emacs, gvim, xemacs, nedit, gimp, etc.

  - Automatically saves changes back to Zope without ending the editing session.

  - Associate any client-side editor application with any Zope object by
    meta-type or content-type. Both text and binary object content can be
    edited.

  - Locks objects while they are being edited. Automatically unlocks them when
    the editing session ends.

  - Can add file extensions automatically to improve syntax highlighting or 
    file type detection.
  
  - Works with basic auth, cookie auth and Zope versions. Credentials are
    automatically passed down to the helper application. No need to
    reauthenticate.
    
  - https support (untested)
  
  Using It

    Use of the application is about as easy as using the ZMI once your browser
    is configured (see the installation instructions). To edit an object
    externally, just click on the pencil icon next to the object in the ZMI.
    The object will be downloaded and opened using the editor application you
    have chosen (you will be prompted the first time to choose an editor). 

    You edit the object just like any other file. When you save the changes in
    your editor, they are automatically uploaded back to Zope in the
    background. While the object is open in your editor, it is locked in Zope
    to prevent concurrent editing. When you end your editing session (ie you
    close your editor) the object is unlocked.

  How it Works
  
    Ok, so this all sounds a bit too good to be true, no? So how the heck does
    it work anyway? First I'll give you a block diagram::
    
      +------------+     +------------+     +---------+        +------+
      | Editor App | <-- | Helper App | <-- | Browser | <-/ /- | Zope |
      +------------+     +------------+     +---------+        +------+
                  ^       ^     ^                                ^
                   \     /       \                              /
                    v   v         -----------------------/ /----
                   -------
                  / Local \
                  \  File /
                   -------
                   
    Now the key to getting this to work is solving the problem that the editor
    cannot know about Zope, and must only deal with local files. Also, there is
    no standard way to communication with editors, so the only communication
    channel can be the local file which contains the object's content or code.
    
    It is trivial to get the browser to fire up your editor when you download
    a particular type of data with your browser. But that does you little good,
    since the browser no longer involves itself once the data is downloaded. It
    just creates a temp file and fires off the registered application, passing
    it the file path. Once the editor is running, it is only aware of the local
    file, and has no concept of where it originated from.
    
    To solve this problem, I have developed a helper application whose job is
    essentially two-fold:
    
    - Determine the correct editor to launch for a given Zope object
    
    - Get the data back into Zope when the changes are saved

    So, let's take a step by step look at how it works:

    1. You click on the external editor link (the pencil icon) in the Zope 
       management interface.
       
    2. The product code on the server creates a response that encapsulates the
       necessary meta-data (URL, meta-type, content-type, cookies, etc) and the
       content of the Zope object, which can be text or binary data. The
       response has the contrived content-type "application/x-zope-edit".

    3. The browser receives the request, and finds our helper application
       registered for "application/x-zope-edit". It saves the response data 
       locally to disk and spawns the helper app to process it.

    4. The helper app, reads its config file and the response data file. The
       meta-data from the file is parsed and the content is copied to a new
       temporary file. The appropriate editor program is determined based on
       the data file and the configuration (or alternately by asking the user).
       
    5. The editor is launched as a sub-process of the helper app, passing it the
       file containing the content data.
       
    6. If so configured, the helper app sends a WebDAV lock request back to Zope
       to lock the object.
       
    7. Every so often (if so configured), the helper app stats the content file
       to see if it has been changed. If so, it sends an HTTP PUT request
       back to Zope containing the new data.
       
    8. When the editor is closed, the content file is checked one more time and
       uploaded if it has changed. Then a WebDAV unlock request is sent to Zope.
       
    9. The helper application exits.
    
  Configuration
  
    The helper application supports several configuration options, each of which
    can be triggered in any combination of object meta-type and content-type.
    This allows you to create appropriate behavior for different types of Zope
    objects and content. The configuration file is stored in the file 
    "~/.zope-external-edit" (Unix) or "~\ZopeEdit.ini" (Windows).
    
    The configuration file follows the standard Python ConfigParser format,
    which is pretty much like the old .ini file format from windows. The file
    consists of sections and options in the following format::

      [section 1]
      option1 = value
      option2 = value

      [section 2]
      ...
    
    Options
    
      The available options for all sections of the config file are:

      editor -- Command line used to launch the editor application. On
      Windows, if no editor setting is found for an object you edit, the
      helper app will search the file type registry for an appropriate editor
      based on the content-type or file extension of the object (which can be 
      specified using the extension option below).

      save_interval -- (float) The interval in seconds that the helper 
      application checks the edited file for changes.

      use_locks -- (1 or 0) Whether to use WebDAV locking.

      cleanup_files -- (1 or 0) Whether to delete the temp files created.
      WARNING the temp file coming from the browser contains authentication
      information and therefore setting this to 0 is a security risk,
      especially on shared machines. If set to 1, that file is deleted at the
      earliest opportunity, before the editor is even spawned. Set to 0 for
      debugging only.

      extension -- (text) The file extension to add to the content file. Allows
      better handling of images and can improve syntax highlighting.

      temp_dir -- (path) Path to store local copies of object data being
      edited. Defaults to operating system temp directory (new in 0.3).

    Sections
    
      The sections of the configuration file specify the types of objects and
      content that the options beneath them apply to.
      
      There is only one mandatory section '[general]', which should define all
      of the above options. If no other section defines an option for a given
      object, the general settings are used.
      
      Additional sections can apply to a particular content-type or meta-type.
      Since objects often have both, the options are applied in this order of
      precedence.
      
      - '[content-type:text/html]' -- Options by whole content-type come first
      
      - '[content-type:text/*]' -- Options by major content-type come second.
      
      - '[meta-type:File]' -- Options by Zope meta-type are third.

      - '[domain:www.mydomain.com]' -- Options by domain follow. Several
        sections can be added for each domain level if desired (new in 0.3).
      
      - '[general]' -- General options are last.
      
      This scheme allows you to specify an extension by content-type, the
      editor by meta-type, the locking setting by domain and the remaining 
      options under general for a given object.
      
  Integrating with External Editor
  
    The external editor product in zope installs a globally available object
    that can format objects accessible through FTP/DAV for use by the helper
    application. You can take advantage of this functionality easily in your own
    content management applications.
    
    Say you have an FTP editable object, "document", in a Zope folder named
    "my_stuff". The URL to view the object would be::
    
      http://zopeserver/my_stuff/document
      
    The URL to kick off the external editor on this document would be::
    
      http://zopeserver/my_stuff/externalEdit_/document
      
    Now, this may look a bit odd to you if you are used to tacking views on to
    the end of the URL. However, because externalEdit_ is required to work on
    Python Scripts and Page Templates, which swallow the remaining URL subpath
    segments following themselves, you must put the call to externalEdit_
    *directly before* the object to be edited. You could do this in ZPT using
    some TAL in a Page Template like::
    
      <a href='edit' 
         attributes='href string:${container/absolute_url}/externalEdit_/$id'>
         Edit Locally
      </a>

  Conclusion
  
    I hope you enjoy using this software. If you have any comments, suggestions
    or would like to report a bug, send an email to the author:
    
      Casey Duncan
      
      casey_duncan@yahoo.com

--

(c) 2002, Casey Duncan and Zope Corporation. All rights reserved.
