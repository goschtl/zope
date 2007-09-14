function cropImage(crop_x, crop_y, crop_w, crop_h, size_w, size_h, rotation){
    
  var tinyMCE = null;
  var win = window.opener ? window.opener : window.dialogArguments;
  
  
  var render_url = document.getElementById("editimage").getAttribute("value");
  var local_url = 'local.crop.w=' + crop_w +
                  '&local.crop.h=' + crop_h +
                  '&local.crop.x=' + crop_x +
                  '&local.crop.y=' + crop_y;
  var remote_url = 'remote.adjust.rotate=' + 0 + rotation +
                   '&remote.size.w=' + size_w +
                   '&remote.size.h=' + size_h; 
  var lastLoadTime = 3000; // TODO: what the f... is the lastLoadTime for????
  
  
	var url = render_url + '/processed?' +	local_url + '&' + remote_url + 
      '&load_' + lastLoadTime + '&stamp=' + (new Date).getTime();
  
  if (!win)
      win = top;
  
  //alert(url);
  
  window.opener = win;
  this.windowOpener = win;
  
  // Setup parent references
  tinyMCE = win.tinyMCE;
  
  if (this.windowOpener.z3cReferenceCurrent != null) {
      obj = document.createElement('img');
      obj.setAttribute('src',url);
      win.z3cReferenceChoosen(obj);
      window.close();
      return false;
  }
      
  var html = '<img ';
  html += 'src="'+url+'"';
  html += ' />';
  tinyMCE.execCommand("mceInsertContent", false, html);
      
  // delete cookie
  var cookie_date = new Date();
  cookie_date.setTime(cookie_date.getTime()-1);
  
  window.close();
} 
  
function getQueryAttrib(variable) {
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
      var pair = vars[i].split("=");
      if (pair[0] == variable) {
          return pair[1];
      }
  } 
  alert('Query Variable ' + variable + ' not found');
}

var query = window.location.search.substring(1);
if (query) {
  var info = {
    "local" : {
      "crop" : {
        "y" : getQueryAttrib('local.crop.y'),
        "x" : getQueryAttrib('local.crop.x'),
        "w" : getQueryAttrib('local.crop.w'),
        "h" : getQueryAttrib('local.crop.h')
      }
    },
    "remote" : {
      "adjust" : {
        "hue" : 0,
        "saturation" : 50,
        "rotate" : getQueryAttrib('remote.adjust.rotate'),
        "brightness" : 0,
        "sharpness" : 0,
        "contrast" : 0},
        "effect" : {
          "grayscale":false
        },
        "size" : {
          "h" : getQueryAttrib('remote.size.h'),
          "w" : getQueryAttrib('remote.size.w')
        }
      },
      "id":1,
      "original" : {
        "size":{
          "h" : orgH,
          "w" : orgW
        }
      }
    };
} else {
  var info = {
    "local" : {
      "crop" : {
        "y" : 0,
        "x" : 0,
        "w" : orgW,
        "h" : orgH
      }
    },
    "remote" : {
      "adjust" : {
        "hue" : 0,
        "saturation" : 50,
        "rotate" : 0,
        "brightness" : 0,
        "sharpness" : 0,
        "contrast" : 0
      },
      "effect" : {
        "grayscale" : false
      },
      "size" : {
        "h" : orgH,
        "w" : orgW
      }
    },
    "id" : 0,
    "original" : {
      "size" : {
        "h" : orgH,
        "w" : orgW
      }
    }
  };
}

window.onload = function() {
  var WIN = window.opener ? window.opener : window.dialogArguments;
  if (WIN.Z3C_REFERENCE == true){
      // we have z3c_reference loaded, we have to look if we need to constrain size
      if (WIN.z3cReferenceCurrent){
          FORCE_WIDTH = WIN.z3cReferenceCurrent.width;
          FORCE_HEIGHT = WIN.z3cReferenceCurrent.height;
     }
  }
  
  
  var target_id="flash_imageeditor_target";      
  var url=document.getElementById("editimage").getAttribute("value");
  url = escape(url).split("+").join("%2B"); // only required for flash 7!
  
  var so = new SWFObject("/++resource++explorer_resources/swf/z3cimage.swf", 
                          "imgeditor", "100%", "100%", "8", "#cccccc");
                   
  so.addParam("quality", "high");
  so.addParam("align", "middle");
  so.addParam("allowScriptAccess", "sameDomain")
  
  so.addVariable("crop_x", info.local.crop.x);
  so.addVariable("crop_y", info.local.crop.y);
  so.addVariable("crop_w", info.local.crop.w);
  so.addVariable("crop_h", info.local.crop.h);
  so.addVariable("output_w", FORCE_WIDTH);
  so.addVariable("output_h", FORCE_HEIGHT);
  so.addVariable("original_h", orgH);
  so.addVariable("original_w", orgW);
  so.addVariable("url", url);
  
  var success = so.write(target_id);
  if (!success) {
      // flash plugin missing or too old    	
      alert("error: unable to inject flash image editor. \nPlease install latest Flash Plugin");
  }
  
  var out="local: " + info.local.crop.x + ", " + info.local.crop.x + ", " + info.local.crop.w + ", " + info.local.crop.h;
  out+="\nremote: " + info.remote.size.w + ", " + info.remote.size.h;
  out+="\noriginal: " + orgW + ", " + orgH;
  out+="\noutput: " + FORCE_WIDTH + ", " + FORCE_HEIGHT;
  
  //alert(out);
} 