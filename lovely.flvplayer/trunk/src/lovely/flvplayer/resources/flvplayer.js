// flvplayer.js
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
    
    var base_url = findBaseUrl();
    
    // create the instance of the player via swfobject
    var so = new SWFObject(base_url+"playerchooser.swf", flash_id, String(width), String(height), 7, "#FFFFFF");
    
    so.addParam("quality", "high");
    so.addParam("wmode", "transparent");
    so.addParam("align", "middle");
    so.addParam("allowScriptAccess", "sameDomain")
    
    so.addVariable("video", forceEscape(flv_url));
    so.addVariable("autostart", autostart);
    so.addVariable("baseurl", forceEscape(base_url));
    if (preview_url != "") so.addVariable("preview", preview_url);
    
    so.write(target_id);
    
}

/**
    searches the base url of this script because
    the swf files can be loaded relative to that url.
    example: 
     <script src="http://localhost:8080/++skin++VOL/teleport.mediaportal/@@/lovely.flvplayer/flvplayer.js" ... 
     in this case the url for the swf is: 
     http://localhost:8080/++skin++VOL/teleport.mediaportal/@@/lovely.flvplayer/playerchooser.swf
     
     @return    base url string
*/
function findBaseUrl(){
    var tags = document.getElementsByTagName("script");
    for (var i=0; i<tags.length; i++){
        if (tags[i].getAttribute("src")){
            if (tags[i].getAttribute("src").indexOf("flvplayer.js")!=-1){
                var base_url = tags[i].getAttribute("src").split("flvplayer.js")[0];
                return base_url;
            }
        }
    }
    
    alert("ERROR: flvplayer.swf unable to calculate baseUrl");
}


/**
    escapes the url including all ++ 
*/
function forceEscape(url){
    return escape(url).split("+").join("%2B");
}
