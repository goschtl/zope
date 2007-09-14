var Z3C_REFERENCE = true;
var z3cReferenceCurrent = null;
var z3cExplorerWindow = null;

function z3cReferenceLinkChoosen(current,ref){
    var current = $(current);
    var ref = $(ref);
    var href = ref.attr('href');
    var title = ref.attr('title');
    current.attr('href',href);
    if(title!=null){
        current.attr('title',title);
        current.html(title);
    }

    // remove the ".tag" suffix
    var fieldId = current[0].id.substr(0,current[0].id.length-4);

    // cant get element with jquery sorry
    var f = document.getElementById(fieldId);
    f.value = href;
}

function z3cReferenceImageChoosen(current,ref){
    var current = $(current);
    var ref = $(ref);
    var src = ref.attr('src');
    var title = ref.attr('title');
    current.attr('src',src);
    if(title!=null){
        current.attr('title',title);
    }
    
    // remove the ".tag" suffix
    var fieldId = current[0].id.substr(0,current[0].id.length-4);
    
    // cant get element with jquery sorry
    var f = document.getElementById(fieldId);
    f.value=src;
}


function z3cReferenceChoosen(ref){
    if (!z3cReferenceCurrent){
        alert("No Object selected!");
    }
    var current = z3cReferenceCurrent;
    z3cReferenceCurrent=null;
    switch (current.tagName) {
    case "A":
        return z3cReferenceLinkChoosen(current,ref);
    case "IMG":
        return z3cReferenceImageChoosen(current,ref);
    }
    alert("Wrong Object returned: " + ref);
}

function z3cReferenceOpenWindow(theURL) {
    var str = "left=0,screenX=0,top=0,screenY=0";

    if (window.screen) {
      var ah = screen.availHeight;
      var aw = screen.availWidth;
      str += ",height=" + ah;
      str += ",innerHeight=" + ah;
      str += ",width=" + aw;
      str += ",innerWidth=" + aw;
    } 
    else {
      str += ",resizable"; // so the user can resize the window manually
    }

    return window.open(theURL, 'explorer', str);
}



function z3cReferenceLinkHandler(obj) {
	var linkElm, imageElm, inst;
  var explorerLink = obj.getAttribute('z3c:explorerLink');
	switch (obj.tagName) {
    case "A":
        return z3cReferenceOpenWindow
            (explorerLink);
    case "IMG":
        var url = obj.getAttribute('src');
        // todo check image on placeholder
        if (url=='/@@/z3c.reference.resources/noimage.jpg' || url=='undefined' || url=='Deleted Object') {
            
            return z3cReferenceOpenWindow
                ('@@explorer.html?link=0');
        } else {
            var url = url.split('/processed?');
            var win = z3cReferenceOpenWindow
                (url[0]+'/@@imgedit.html?'+url[1]);
        } 
	}
	return false; // Pass to next handler in chain
}


function z3cReferenceOnClick(obj,command){
    if (z3cExplorerWindow){
        z3cExplorerWindow.close();
        z3cExplorerWindow=null;
        z3cReferenceCurrent=null;
    }
    z3cExplorerWindow = z3cReferenceLinkHandler(obj);
    z3cReferenceCurrent=obj;
    return false;
}

