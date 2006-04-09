

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
            if (response[0] == '{') {
                var event = JSON.parse(response);
                var name = event['name'];
                name = "on" + name[0].toUpperCase() + name.slice(1);
                LivePage.Responders.dispatch(name, event);
                }
                
			setTimeout("LivePage.nextEvent()", 500);
			return true;
			}
	   },
	
    
    nextEvent : function () {
        var base_url = LivePage.baseURL + "/@@output/" + LivePage.uuid;
        lastRequest = new Ajax.Request(base_url, 
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

    stopClient : function() {
        LivePage.sendEvent({name: "close", uuid: LivePage.uuid });
        },


    sendEvent : function (event) {
        var params = ""
        for(key in event) {
            params += "&" + key + "=" + event[key]
            }
        var base_url = LivePage.baseURL + "/@@input/" + LivePage.uuid;
        
        new Ajax.Request(base_url, 
            { method: 'post',
                parameters: params
            });
        LivePage.numSended += 1;
        if ($('event_count')) {
            $('event_count').innerHTML = LivePage.numSended;
            }
        return true;
        },

    getAttention : function (act, id) {
        if (act) {
            switch(act) {
                case 'scroll' : {
                    LivePage.scrollToLast(id);
                    LivePage.highlightElement(id);
                    return;
                    }
                case 'sound' : {
                    LivePage.playFlash("ping");
                    return;
                    }
                }
            }
        },
   
    scrollToLast : function (id) {
        var area = $(id);
        if (area.offsetHeight > area.scrollHeight) {
            area.scrollTop = 0;
            } else {
            area.scrollTop = area.scrollHeight;
            }
        },
        
    highlightElement : function (id) {
        return;
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
        } catch (e) { alert(e); }
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
            $(id).innerHTML += html;  /* .stripScripts(); */
            /* We must eval all scripts again. Arrgh!   */
            $(id).innerHTML.evalScripts();
           
            // LivePage.getAttention($(id).lastChild.id, event.extra);
            return;
            },
                
    onUpdate : function(event) {
            var id = event['id'];
            var html = event['html'];
            $(id).innerHTML = html;
            html.evalScripts();
            LivePage.getAttention(id, event.extra);
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
            }
            
    }
            

