function lovelyFlashUploadStartBrowsing(){
    // tells flash to start with browsing
    if(window.fuploader){
        window.document["fuploader"].SetVariable("startBrowse", "go");
    }else if(document.fuploader){
        document.fuploader.SetVariable("startBrowse", "go");
    }         
}

function lovelyFlashUploadDisableBrowseButton(){
    $("flash.start.browsing").style.visibility = "hidden";
    $("flash.start.browsing").disabled = "disabled";
}

function lovelyFlashUploadOnUploadCompleteFEvent(status){
    // always fired from flash
    if (typeof(lovelyFlashUploadOnUploadComplete) == "function"){
        lovelyFlashUploadOnUploadComplete(status);
    }
}

function lovelyFlashUploadOnFileCompleteFEvent(filename){
    // always fired from flash
    if (typeof(lovelyFlashUploadOnFileComplete) =="function"){
        lovelyFlashUploadOnFileComplete(filename);
    }
}

/**
    called when the user presses the cancel button while browsing
*/  
function lovelyFlashUploadOnCancelFEvent(){
    if (typeof(lovelyFlashUploadOnCancelEvent) =="function"){
        lovelyFlashUploadOnCancelEvent(filename);
    }    
}

/**
    called if an error occured during the upload progress 
*/
function lovelyFlashUploadOnErrorFEvent(error_str){
    if (typeof(lovelyFlashUploadOnErrorEvent) =="function"){
        lovelyFlashUploadOnErrorEvent(error_str);
    }    
}
/**
    creates a instance of the multifile upload widget
    insidde the target div. 
    Required global variable: swf_upload_target_path
*/
function createFlashUpload(){
    var so = new SWFObject(swf_upload_url, "fuploader", "300", "100", "#f8f8f8");
    so.addParam("allowScriptAccess", "sameDomain");
    so.addParam("wmode", "transparent");
    
    // we need to manually quote the "+" signs to make shure they do not
    // result in a " " sign inside flash    
    var quoted_location_url =   escape(window.location.href).split("+").join("%2B");
    so.addVariable("target_path", swf_upload_target_path);
    so.addVariable("base_path", quoted_location_url);
    
    so.write("flashuploadtarget");
}

Event.observe(window, "load", createFlashUpload, false);     
