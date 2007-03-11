/**

    creates a flash flv video player instance.
    
    please give all parameters as an object.
    
    example:
    createFLVPlayer({target_id:"flash_dom_target_id",
                     flv_url:"myvideo.flv",
                     width:300,
                     height:250,
                     autostart:true});
    
    possible parameters:
    @param  target_id:String
    @param  flv_url:String
    @param  preview_url:String (optional) url to the preview image. 
    @param  width:Number (optional default: 450)
    @param  height:Number (optional default: 338)
    @param  autostart:Boolean (optional. default: false);
    @param  flash_id:String (optional. default: "videoplayer") the dom id of the swf object.
    @author <manfred.schwendinger@lovelysystems.com>    
*/


function createFLVPlayer(obj){
    
    // set default values
    var target_id = "";
    var flv_url = "";
    var width = 450;
    var height = 368;
    var autostart = "0";
    var flash_id = "videoplayer";
    var preview_url = "";
    var fullscreen = "0";
    var ad_url = "";    // url which should be played before playing the video (swf or flv)
    var ad_target = ""; // url that should be loaded in a new window if someone clicks onto the swf. 
    
    // check for required params
    if (obj["target_id"] == undefined) alert("ERROR: createFLVPlayer failed. target dom id is missing"); 
    else target_id = obj.target_id;   
    if (obj["flv_url"] == undefined) alert("ERROR: createFLVPlayer failed. no flv video url is given");
    else flv_url = obj.flv_url;
    
    
    // check for optional params
    if (obj["width"]) width = obj.width;
    if (obj["height"]) height = obj.height;
    if (obj["autostart"]) autostart = obj.autostart==true ? "1" : "0";
    if (obj["flash_id"]) flash_id = obj.flash_id;
    if (obj["preview_url"]) preview_url = obj.preview_url;
    if (obj["ad_url"]) ad_url = obj.ad_url;
    if (obj["ad_target"]) ad_target = obj.ad_target; 
     
    var base_url = findBaseUrl();
    
    var so = new SWFObject(base_url+"@@/flvplayer.swf",
                           flash_id,
                           String(width), String(height),
                           "8", "#FFFFFF");
    
    so.addParam("quality", "high");
    so.addParam("wmode", "transparent");
    so.addParam("align", "middle");
    so.addParam("allowScriptAccess", "sameDomain")
    
    so.addVariable("video", flv_url);
    so.addVariable("autostart", autostart);
    so.addVariable("baseurl", base_url);
    
    if (preview_url != "") so.addVariable("preview", preview_url);
    if (obj.fullscreen)    so.addVariable("fullscreen", "1");
    if (ad_url != "")      so.addVariable("ad_url", ad_url);
    if (ad_target != "")   so.addVariable("ad_target", ad_target);
    
    var success = so.write(target_id);
    if (!success){
        // flash plugin missing or too old
        $("#"+target_id).load("noflashdetected.html");
    }
}

/**
    searches the base url of this script because
    the swf files can be loaded relative to that url.
    example: 
     <script src="http://localhost:8080/++skin++VOL/teleport.mediaportal/@@/lovely.flvplayer/flvplayer.js" ... 
     in this case the url for the swf is: 
     http://localhost:8080/++skin++VOL/teleport.mediaportal/@@/lovely.flvplayer/flvplayer.swf
     
     @return    base url string
*/

function findBaseUrl(){
    var tags = document.getElementsByTagName("script");
    for (var i=0; i<tags.length; i++){
        if (tags[i].getAttribute("src")){
            if (tags[i].getAttribute("src").indexOf("flvplayer.js")!=-1){

                var base_url = tags[i].getAttribute("src").split("flvplayer.js")[0];
                base_url = base_url.split("@@")[0]
                
                return base_url;
            }
        }
    }
    
    alert("ERROR: flvplayer.swf unable to calculate baseUrl");
}

/**
    escapes the url including all ++ 
    this is required for flash 7
*/
/*
function forceEscape(url){
    return url;
    //return escape(url).split("+").join("%2B");
}
*/

function openFullScreenView(video_url){ 
    
    var wOpen;
    var sOptions;
    
    sOptions = 'status=no,menubar=no,scrollbars=no,resizable=yes,toolbar=no';
    sOptions = sOptions + ',width=' + (screen.availWidth - 10).toString();
    sOptions = sOptions + ',height=' + (screen.availHeight - 122).toString();
    sOptions = sOptions + ',screenX=0,screenY=0,left=0,top=0';


    
    var url = findBaseUrl() + '@@/lovely.flvplayer/videofullscreen.html?url='+
        video_url;
    
    
    wOpen = window.open(url, 'videofullscreen',  sOptions );
    wOpen.focus();
    wOpen.moveTo( 0, 0 );
    wOpen.resizeTo( screen.availWidth, screen.availHeight );
    
}