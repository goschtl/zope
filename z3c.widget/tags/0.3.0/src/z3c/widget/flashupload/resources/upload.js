function z3cFlashUploadStartBrowsing(){
    // tells flash to start with browsing
    if(window.fuploader){
        window.document["fuploader"].SetVariable("startBrowse", "go");
    }else if(document.fuploader){
        document.fuploader.SetVariable("startBrowse", "go");
    }
}

function z3cFlashUploadEnableBrowseButton(){
    document.getElementById("flash.start.browsing").style.visibility = "visible";
    document.getElementById("flash.start.browsing").disabled = false;
}

function z3cFlashUploadDisableBrowseButton(){
    document.getElementById("flash.start.browsing").style.visibility = "hidden";
    document.getElementById("flash.start.browsing").disabled = "disabled";
}

function z3cFlashUploadOnUploadCompleteFEvent(status){
    // always fired from flash
    if (typeof(z3cFlashUploadOnUploadComplete) == "function"){
        z3cFlashUploadOnUploadComplete(status);
    }
}

function z3cFlashUploadOnFileCompleteFEvent(filename){
    // always fired from flash
    if (typeof(z3cFlashUploadOnFileComplete) =="function"){
        z3cFlashUploadOnFileComplete(filename);
    }
}

/**
    called when the user presses the cancel button while browsing
*/
function z3cFlashUploadOnCancelFEvent(){

    if (typeof(z3cFlashUploadOnCancelEvent) =="function"){
        z3cFlashUploadOnCancelEvent();
    }
}

/**
    called if an error occured during the upload progress
*/
function z3cFlashUploadOnErrorFEvent(error_str){
    if (typeof(z3cFlashUploadOnErrorEvent) =="function"){
        z3cFlashUploadOnErrorEvent(error_str);
    }
}

function prepareUrlForFlash(url){
    return escape(url).split("+").join("%2B");
}
/**
    creates a instance of the multifile upload widget
    insidde the target div.
    Required global variable: swf_upload_target_path
*/
function createFlashUpload()
{
    var so = new SWFObject(swf_upload_url, "fuploader", "100%", "100%", "8.0.33", "#f8f8f8");
    so.addParam("allowScriptAccess", "sameDomain");
    so.addParam("wmode", "transparent");

    // we need to manually quote the "+" signs to make sure they do not
    // result in a " " sign inside flash

    so.addVariable("target_path", swf_upload_target_path);
    so.addVariable("site_path", prepareUrlForFlash(swf_upload_site_url));
    so.addVariable("config_path", prepareUrlForFlash(swf_upload_config_url));

    var success = so.write("flashuploadtarget");

    if (!success){
        $("#flashuploadtarget").load("noflashupload.html")
    }
}


if (window.addEventListener){
    window.addEventListener('load', createFlashUpload, false);
}
else if(window.attachEvent){
    window.attachEvent('onload', createFlashUpload);
}
