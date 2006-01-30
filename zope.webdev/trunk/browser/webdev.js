function switchDisplay(id, url) {

    if(document.getElementById) {
       // DOM
       var element = document.getElementById(id);
    } else {
        if(document.all) {
            // Proprietary DOM
            var element = document.all[id];
        } else {
            // Create an object to prevent errors further on
            var element = new Object();
        }
    }

    if(!element) {
        /* The page has not loaded or the browser claims to support
        document.getElementById or document.all but cannot actually
        use either */
        return;
    }

    // Reference the style ...
    if (element.style) {
        style = element.style;
    }

    if (typeof(style.display) == 'undefined' &&
        !( window.ScriptEngine && ScriptEngine().indexOf('InScript') + 1 ) ) {
        //The browser does not allow us to change the display style
        //Alert something sensible (not what I have here ...)
        window.alert( 'Your browser does not support this' );
        return;
    }

   // Change the display style
   if (style.display == 'none') {
       style.display = '';
       switchImage(id, 'collapsed.png', 'expanded.png');
   }
   else {
       style.display = 'none';
       switchImage(id, 'expanded.png', 'collapsed.png');
   }
   saveSwitch(id, url);
}

function switchImage(id, oldname, newname) {
    if(document.getElementById) {
       // DOM
       var element = document.getElementById(id+'.switcher');
    } else {
       // Proprietary DOM
       var element = document.all[id+'.switcher'];
    }
    element.src = element.src.replace(oldname, newname);
}

function saveSwitch(id, url) {
    var names = id.split('*');
    managerName = names[0];
    viewletName = names[1];
    var req = new XMLHttpRequest();
    req.open("POST",
             url+'/++pagelets++'+managerName+'/'+viewletName+'/@@switch.html',
             false);
    req.send(null);
}
