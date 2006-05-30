

var LivePage = {
    uuid: "",
    baseURL: "",
    numErrors: 0,
    userAgent : navigator.userAgent.toLowerCase(),
    lastRequest : null,
    alreadyEvaluated : {},
    numSended: 0,

    ajaxHandlers : {
        onError: function(request, transport) {
            LivePage.numErrors += 1;
			LivePage.lastRequest = null;
            if (LivePage.numErrors > 3) {
                alert("Too much errors. The page will be reloaded.");
                window.location.reload();
                }
            else if (LivePage.numErrors > 1) {
                if (confirm('An error occured. Reload page?')) {
                    window.location.reload();
                    }
                else {
                    setTimeout("LivePage.nextEvent()", 2000);
                    }
                }
            else {
                setTimeout("LivePage.nextEvent()", 500);
                }
            return true;
		},

        onComplete: function(request, transport, json) {
          
            var response = transport.responseText;
            LivePage.lastRequest = null;
            if (response.substr(0,1) == '{') {
                var event = JSON.parse(response);
                if (event.name != 'idle') {
                    LivePage.logging("Event received: " + event.name);
                    }
                LivePage.processEvent(event);
                }
          
			setTimeout("LivePage.nextEvent()", 500);
			return true;
			}
	   },
	   
    processEvent : function (event) 
	    {
        var name = event['name'];
        name = "on" + name.substr(0,1).toUpperCase() + name.slice(1);
        LivePage.Responders.dispatch(name, event);
	    },
    
    nextEvent : function () {
        
        
        if(LivePage.lastRequest){ 
            LivePage.logging("nextEvent blocked");
            return;
        }
        var base_url = LivePage.baseURL + "/@@output/" + LivePage.uuid;
        
        // LivePage.logging("nextEvent " + base_url);
        LivePage.lastRequest = new Ajax.Request(base_url, 
                                { method: 'get', asynchronous:true});
        },

    startClient : function () {
        Ajax.Responders.register(LivePage.ajaxHandlers);
        LivePage.Responders.register(LivePage.clientHandlers);
        if (!LivePage.baseURL) {
            LivePage.baseURL = window.location.href;
            var i = LivePage.baseURL.indexOf('#');
            if (i != -1) {
                LivePage.baseURL = LivePage.baseURL.substring(0, i);
                }
            setTimeout("LivePage.nextEvent()", 500);
            return true;
            }
        else {
            alert("startClient called again...");
            }
        },
        
    
    callInProgress : function(xmlhttp) {
        switch (xmlhttp.readyState) {
            case 1: case 2: case 3:
                return true;
            break;
            // Case 4 and 0
            default:
                return false;
            break;
            }
        },


    stopClient : function() {
        if (self.lastRequest) {
            if (LivePage.callInProgress(self.lastRequest.transport)) {
                self.lastRequest.transport.abort();
                }
            }
        
        LivePage.sendEvent({name: "close", uuid: LivePage.uuid });
        },


    sendEvent : function (event) {
//        alert("entered sendEvent ... event = " + event);
        var params = ""
        for(key in event) {
            params += "&" + key + "=" + event[key]
            }
//        alert("params = " + params);
        var base_url = LivePage.baseURL + "/@@input/" + LivePage.uuid;
//        alert("base_url = " + base_url);


        new Ajax.Request(base_url, 
            { method: 'post',
                parameters: params,
                asynchronous: true
            });

//        alert("request sended");

        LivePage.numSended += 1;
        if ($('event_count')) {
            $('event_count').innerHTML = LivePage.numSended;
            }
        return true;
        },

  

    scrollToLast : function (id) {
        var scrollArea = $(id).parentNode;
        var scrollAreaId = $(id).parentNode.lastChild.previousSibling.getAttribute('id');
        document.getElementById(scrollAreaId).scrollIntoView(true);
        },

    scrollToNew : function (id) {
        document.getElementById(id).scrollIntoView(true);
        if ((navigator.appName.substr(0,1).toLowerCase()) == "m")
            {
            window.scrollBy(-300,0);
            }
        },

        
    highlightElement : function (id, start, end) {
        if (start && end) {
            new Effect.Highlight(id, {startcolor:start, endcolor:end});
            }
        else {
            new Effect.Highlight(id);
            }
        },

    playSound : function (id) {
        playFlash(id);
        },
        
    logging : function(str) {
        if ($('logging')) {
            $('logging').innerHTML += "<p>" + str + "</p>"
            }
        }

}

LivePage.Responders = {
  responders: [],

  _each: function(iterator) {
    this.responders._each(iterator);
  },

  register: function(responderToAdd) {
    if (!this.include(responderToAdd))
      this.responders.push(responderToAdd);
  },

  unregister: function(responderToRemove) {
    this.responders = this.responders.without(responderToRemove);
  },

  dispatch: function(callback, event) {
    this.each(function(responder) {
      if (responder[callback] && typeof responder[callback] == 'function') {
        try {
          responder[callback].apply(responder, [event]);
        } catch (e) { alert ("exception thrown at: " + callback); }
      }
    });
  }
};


Object.extend(LivePage.Responders, Enumerable);

LivePage.clientHandlers = {
    /* Basic LivePage handlers that can be extended via
       registrations to LivePage.Responders */
     
    onReload: function(event) {
            alert("The connection has been interrupted. The page will be reloaded.");
            window.location.reload();
            return;
            },
            
    onAppend: function(event) {            
            var id = event['id'];
            var html = event['html'];
//            alert("append: " + id + " --- " + html);
            $(id).innerHTML += html;  /* .stripScripts(); */
            /* We must eval all scripts again. Arrgh!   */
            $(id).innerHTML.evalScripts();
            return;
            },
                
    onScroll: function(event) {            
            var id = event['id'];
            LivePage.scrollToNew(id);
            return;
            },

    onHighlight: function(event) {            
            var id = event['id'];
            var start = event['start'];
            var end = event['end'];
            LivePage.highlightElement(id, start, end);
            return;
            },


    onSound: function(event) {            
            var id = event['id'];
            LivePage.playSound(id);
            return;
            },


    onUpdate : function(event) {
            var id = event['id'];
            var html = event['html'];
            LivePage.logging("update: " + id);
            $(id).innerHTML = html;
//            html.evalScripts();
//            id.evalScripts();
            $(id).innerHTML.evalScripts();
            return;
            },
            
    onIdle : function(event) {
            if ($("livepage_status")) {
                $("livepage_status").innerHTML = "idle";
                }
            return;
            },
            
    onProgress : function(event) {
            if ($("livepage_progress")) {
                $("livepage_progress").innerHTML = event.percent + "%";
                }
            return;
            },


    onMulti: function(event) {
            allEvents = event.events;
            for (i=0; i<allEvents.length; i++)  
                {
                var event = allEvents[i]; 
                LivePage.processEvent(event);
                }
            return;
            }
    }
            

