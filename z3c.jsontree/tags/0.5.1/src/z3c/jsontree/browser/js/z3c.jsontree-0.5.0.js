//----------------------------------------------------------------------------
/** 
 * @fileoverview JSON loading unordered list based tree 
 * 
 * @author Roger Ineichen dev at projekt01 dot org.
 * @version Initial, not documented 
 */
//----------------------------------------------------------------------------
/* zrt-replace: "./z3cJSONTreeIMG" tal"string:${context/++resource++z3cJSONTreeIMG}" */

/* Note: this script uses z3c.xmlhttp.js and z3c.jsonrpcproxy.js */
/* TODO: use metadata plugin for get/set the json loader uri */

//----------------------------------------------------------------------------
// public API
//----------------------------------------------------------------------------

(function($) {
$.fn.z3cJSONTree = function (settings) {
	settings = $.extend({
        z3cJSONTreeCollapsedGif: './z3cJSONTreeIMG/z3cJSONTreeCollapsed.gif',
        z3cJSONTreeExpandedGif: './z3cJSONTreeIMG/z3cJSONTreeExpanded.gif',
        z3cJSONTreeStaticGif: './z3cJSONTreeIMG/z3cJSONTreeStatic.gif',
        z3cJSONTreeCollapsedClass: 'z3cJSONTreeCollapsed',
        z3cJSONTreeExpandedClass: 'z3cJSONTreeExpanded',
        z3cJSONTreeStaticClass: 'z3cJSONTreeItem',
        z3cJSONTreeIconClass: 'z3cJSONTreeIcon',
        loadItemsMethodName: 'loadJSONTreeItems'
	}, settings);

    function z3cJSONTreeToggleItem(img) {
        ele = img.parentNode;
        var uri = $(img).attr('longDesc');
        if ($.className.has(ele, settings.z3cJSONTreeExpandedClass)) {
            ele.className = settings.z3cJSONTreeCollapsedClass;
            $(img).attr("src", settings.z3cJSONTreeCollapsedGif);
        }
        else {
            /* check for sub items */
            if ($(ele).find('li').length == 0){
                /* load childs from server via JSON */
                id = $(ele).attr('id');
                z3cJSONTreeLoadItems(uri, id);
            }
            ele.className = settings.z3cJSONTreeExpandedClass;
            $(img).attr("src", settings.z3cJSONTreeExpandedGif);
        }
        return false;
    }

    function z3cJSONTreeLoadItems(uri, id) {
        /* each different json tree uses a own function for calling the childs */
        loader = settings.loadItemsMethodName;
    	var jsonProxy = new JSONRPC(uri);
    	jsonProxy.addMethod(loader, z3cJSONTreeAddItems, id);
        /* call the child loader method */
        var loaderMethod = jsonProxy[loader];
    	loaderMethod(id);
    }
    
    function z3cJSONTreeAddItems(response, requestId) {
        var res = response['treeChilds'];
        var childs = res['childs'];
        ele = document.getElementById(res['id']);
        var ele = $(ele);
        var ul = null;
        
        /* find ul tag which will contain the new childs */
        var ul = ele.find('ul')[0]
        if (!ul){
            ele.append('<ul></ul>')
        }
        var ul = ele.find('ul')[0]
        
        /* render and append the new childs to the existing empty <ul> tag */
        for (var i=0; i<childs.length; i++) {
            var itemInfo = childs[i];
            var iconSrc = itemInfo['iconURL'];
            var hasChilds = itemInfo['hasChilds'];
            var linkHandler = itemInfo['linkHandler'];
            var contextURL = itemInfo['contextURL'];

            /* create toggle icon */
            if (iconSrc != '') {
                var icon = $('<img></img>');
                icon.attr("src", iconSrc);
            }
            /* create li tag */
            var li = $('<li></li>');
            li.attr("id", itemInfo['id']);

            /* create toggle image */
            var img = $('<img></img>');;
            img.attr("width", "16");
            img.attr("height", "16");
            if (hasChilds) {
                img.className = settings.z3cJSONTreeIconClass;
                img.attr('longDesc', contextURL);
                img.click(function(){
                    z3cJSONTreeToggleItem(this)
                });
                img.attr("src", settings.z3cJSONTreeCollapsedGif);
                li.className = settings.z3cJSONTreeCollapsedClass;
            }
            else{
                li.className = settings.z3cJSONTreeStaticClass;
                img.attr("src", settings.z3cJSONTreeStaticGif);
            }
            /* create link or handler */
            var a = $('<a href=""></a>');
            if (linkHandler != '') {
                a.click(eval(linkHandler));
                a.attr("href", '#');
            }else {
                a.attr("href", itemInfo['url']);
            }
            /* append content to link */
            a.html(itemInfo['content']);
            li.append(a);
            /* append link to  to link */
            if (iconSrc != '') {
                icon.insertBefore(a);
                img.insertBefore(icon);
            }
            else {
                img.insertBefore(a);
            }
            $(ul).append(li);
        }
    }

    // render tree
    function renderTree(ul) {
        if ($(ul).length == 0) {
            return;
        }
        for (var i=0; i<ul.childNodes.length; i++) {
            var item = ul.childNodes[i];
            if (item.nodeName == "LI") {
                for (var si=0; si<item.childNodes.length; si++) {
                    var subitem = item.childNodes[si];
                    if (subitem.nodeName == "UL") {
                        renderTree(subitem, false);
                    }
                }
                img = $(item.firstChild);
                img.click(function(){
                    z3cJSONTreeToggleItem(this)
                });
            }
        }
    }

    // initialize json trees
    return $(this).each(function(){
        renderTree(this);
    });
};
})(jQuery);
