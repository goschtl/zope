function z3cFlashUploadStartBrowsing(){
    // tells flash to start with browsing
    if(window.fuploader){
        window.document["fuploader"].SetVariable("startBrowse", "go");
    }else if(document.fuploader){
        document.fuploader.SetVariable("startBrowse", "go");
    }         
}

function z3cFlashUploadDisableBrowseButton(){
    $("flash.start.browsing").style.visibility = "hidden";
    $("flash.start.browsing").disabled = "disabled";
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
/**
    creates a instance of the multifile upload widget
    insidde the target div. 
    Required global variable: swf_upload_target_path
*/
function createFlashUpload(){
    var so = new SWFObject(swf_upload_url, "fuploader", "300", "100", "8.0.33", "#f8f8f8");
    so.addParam("allowScriptAccess", "sameDomain");
    so.addParam("wmode", "transparent");
    
    // we need to manually quote the "+" signs to make shure they do not
    // result in a " " sign inside flash    
    var quoted_location_url =   escape(window.location.href).split("+").join("%2B");
    so.addVariable("target_path", swf_upload_target_path);
    so.addVariable("base_path", quoted_location_url);
    
    var success = so.write("flashuploadtarget");
    if (!success){
       	
        var ajaxUpdater = new Ajax.Updater(
			"flashuploadtarget", 
			'noflashupload.html', 
			{
				method: 'get'
			});
			   
			/*
        // flash plugin missing or too old
        var error_msg = "<div class=\"flash-detection-error\">Flash Player detection failed. ";
        error_msg += "Please install the Flash Player Plugin. You can install the plugin ";
        error_msg += "<a href=\"http://www.adobe.com/go/getflashplayer\">here</a> for free.</div>";
        document.getElementById(target_id).innerHTML = error_msg;    
        */
    }
}

Event.observe(window, "load", createFlashUpload, false);     
