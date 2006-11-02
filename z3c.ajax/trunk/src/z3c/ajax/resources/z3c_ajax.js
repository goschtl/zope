Array.prototype.indexOf = function(v) {
    for(var i = 0; i < this.length; i++) if(this[i] == v) return i; return -1;
}

Array.prototype.remove = function(v) {
    for(var i = 0; i < this.length; i++) if(this[i] == v) { this.splice(i, 1); return; }
}

// Adds event to window.onload without overwriting currently 
// assigned onload functions.
function addLoadEvent(func)
{
    var oldonload = window.onload;
    if (typeof window.onload != 'function')
    {
        window.onload = func;
    } 
    else 
    {
        window.onload = function()
        {
            oldonload();
            func();
        }
    }
}

var z3cContainerOnLoadListeners = Array();
function z3cContainerLoaded(container){
    //alert(z3cContainerOnLoadListeners.length);
    z3cContainerOnLoadListeners.each(function(f){
            f(container);
        });
}


function z3cAddContainerLoadListener(func){
    z3cContainerOnLoadListeners.push(func);
}

function z3cRemoveContainerLoadListener(func){
    z3cContainerOnLoadListeners.remove(func);
}

function fnSuccess(t){
    //alert(t.responseText);
}

function fnFailure(resp){
    alert('failure: ' + t.responseText);
}

var z3cAjaxContainerCount=0;

// returns the next parent of obj which has the given class
function z3cNextParentByClass(obj,klass){
    obj = $(obj);
    
    while(!Element.hasClassName(obj,klass)){
        if (obj.parentNode==document){
            return null;
        }
        obj=obj.parentNode;
    }
    if (obj){
        return obj;
    }
    return null;
}

function z3cIsContainer(obj){
    obj = $(obj);
    return (obj.getAttribute('class')=='ajax:container');
}

function z3cNextContainer(obj){

    obj = $(obj);
    while(obj && (!z3cIsContainer(obj))){
        obj=obj.parentNode;

    }
    if (z3cIsContainer(obj)){
        return obj;
    }
    return null;
}

function z3cContainerURL(obj,view){
    var container = z3cNextContainer(obj);
    var current = container.getAttribute('ajax:src');
    return current.substr(0,current.lastIndexOf('/')+1) + view;
}

// calls an url on the container
function z3cCallContainer(obj,view,callback){
    var container = z3cNextContainer(obj);
    var url = z3cContainerURL(obj,view);
    new Ajax.Request(url,
                     {asynchronous:true,
                             method: 'get',
                             onSuccess: fnSuccess,
                             onFailure: fnFailure,
                             onComplete: callback,
                             evalScripts:true}
                     );
    //alert('loaded');
}


function z3cChangeView(obj,view,condition){
    if ((condition != null)&&(!condition)){
        return;
    }
    var container = z3cNextContainer(obj);
    var url = z3cContainerURL(container,view);
    z3cLoadContainer(container,url);
}

function z3cLoadContainer(container,url,paras){
    // XXX: this should be a class because of the onComplete func
    var container=$(container);

    if (!url){
        url = container.getAttribute('ajax:src');
    }
    new Ajax.Updater(container.id,
                     url,
                     {asynchronous:true,
                             method: 'get',
                             onSuccess: fnSuccess,
                             onFailure: fnFailure,
                             parameters: paras,
                             onComplete: function (t){
                             return z3cContainerLoaded(container);
                         },
                             evalScripts:true}
                     );
}

// recursive load containers
z3cAddContainerLoadListener(z3cLoadContainers);

function z3cLoadContent(event){
    z3cLoadContainers(document.body);
}

function z3cSaveForm(f){
    var f = $(f);
    var container = z3cNextContainer(f);
    var paras = (Form.serialize(f));
    z3cLoadContainer(container,null,paras);
    return;
    new Ajax.Request(f.action,
                     {asynchronous:false,
                             method: 'get',
                             onSuccess: fnSuccess,
                             onFailure: fnFailure,
                             parameters: paras,
                             evalScripts:true}
                     );
}

function z3cLoadContainers(obj){
    // loads containers in obj
    var obj = $(obj);
    var containers = document.getElementsByClassName('ajax:container',obj);
    for (i=0;i<containers.length;i++) {
        var container = containers[i];
        // make sure we have an id
        if (!container.id){
            z3cAjaxContainerCount++;
            var id='ajax:container:' +z3cAjaxContainerCount;
            container.id=id;
        }
        z3cLoadContainer(container);
    }
}

addLoadEvent(z3cLoadContent);




function makeEdit(id){
    
    var containerId = id + ".container";
    var name = $(containerId).getAttribute('name');
    //var url = document.location + '/@@ajax/' + id;
    var url=$(containerId).getAttribute('url');
    //alert(url);
    var paras = '__input__=1';
    new Ajax.Updater(containerId,
                     url,
                     {asynchronous:true,
                             method: 'get',
                             onSuccess: fnSuccess,
                             onFailure: fnFailure,
                             parameters: paras,
                             evalScripts:true}
                     );
}

function z3cApplyChanges(obj){
    var value = $F(obj);
    z3cChangeView(obj,'display?apply=1&' + obj.name +'='+$F(obj));
}


function applyAndDisplay(id){
    var containerId = id + ".container";
    var url = document.location + '/@@ajax/' + id;
    paras = id +'='+ $F(id) + '&' + id +'.apply=1';
    new Ajax.Updater(containerId,
                     url,
                     {asynchronous:true,
                             method: 'get',
                             parameters: paras,
                             }
                     );

}