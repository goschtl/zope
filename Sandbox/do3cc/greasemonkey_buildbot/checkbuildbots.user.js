// ==UserScript==
// @name           checkbuildbots
// @namespace      http://do3.cc
// @description    For the buildbots page of the zope toolkit, follow each buildbot link, check the status and display the result
// @include        file:///home/patrick/.virtualenvs/zopetoolkit/build/html/process/buildbots.html
// ==/UserScript==
//
//
function retrieveResult(link){
    GM_xmlhttpRequest({
        method : "GET",
        url : link[0].href,
        onload : function(response){
            try //Internet Explorer
            {
              xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
              xmlDoc.async="false";
              xmlDoc.loadXML(response);
            }
            catch(e){
              try // Firefox, Mozilla, Opera, etc.
              {
                parser=new DOMParser();
                xmlDoc=parser.parseFromString(response.responseText,"text/xml");
              }
              catch(e){
                alert(e.message);
                return;
              }
            }
            var reallyBad = false;
            try{
                var success = xmlDoc.getElementsByTagName('ul')[0].childNodes[1].childNodes[2].textContent === 'success';
            } catch(e){
                try{
                     var success = xmlDoc.getElementsByTagName('table')[0].childNodes[1].childNodes[2].childNodes[5].textContent === 'success';
                } catch(e) {
                    try{
                        var success = xmlDoc.getElementsByTagName('table')[0].childNodes[3].childNodes[5].textContent === 'success';
                    } catch(e) {
                        var reallybad = true;
                    }
                }
            }
            if(success){
                link.css('background-color', 'green');
            }else{
                if(reallyBad){
                    link.css('background-color', 'black');
                }else{
                    link.css('background-color', 'red');
                }
            }
        }
    });
};
//
// set up jQuery variable
var $;

// Add jQuery
var GM_JQ = document.createElement("script");
GM_JQ.src = "http://code.jquery.com/jquery-latest.min.js";
GM_JQ.type = "text/javascript";

document.body.appendChild(GM_JQ);

// Check if jQuery's loaded
var checker=setInterval(function(){
    if(typeof ($ = unsafeWindow.jQuery) != "undefined") {
        clearInterval(checker);
        letsJQuery();
    }
},100);

// All your GM code must be inside this function
function letsJQuery() {
    var links = new Array();

    $('div#windows tr, div@linux tr, div#mac-os-x tr').each(function (){
        var fields = $('td', this);
        // We start at 1, because we ignore the first column
        for(var i=1;i<fields.length;i++){
           var link = $('a', fields[i]);
            if(link.length > 0){
                link.each(function(){
                    links.push($(this));
                });
            }
        }
    });
    for (i in links){
        retrieveResult(links[i]);
    }
}

