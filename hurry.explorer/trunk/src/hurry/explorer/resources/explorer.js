// create the top-level PLOR namespace if needed
if (typeof PLOR == "undefined" || !PLOR) {
    var PLOR = {};
}

// create a new namespace (under PLOR)
PLOR.namespace = function(name) {
    var ns = PLOR;
    var parts = name.split(".");
    if (parts[0] == "PLOR") {
        parts = parts.slice(1);
    }
    for (var i = 0; i < parts.length; i++) {
        var part = parts[i];
        ns[part] = ns[part] || {};
        ns = ns[part];
    }
    return ns;
};

(function() {
    // the explorer namespace
    PLOR.namespace("explorer");
    
    //*** private variables
    var tabs = null;
    var tree = null;
    var datatable = null;

    //*** private functions

    // load data for subnodes in a tree node
    var loadNodeData = function(node, fnLoadComplete) {
        var nodepath = encodeURI(node.data.path);
        
        var callback = {
            success: function(oResponse) {
                var results = YAHOO.lang.JSON.parse(oResponse.responseText);
                var length = results.nodes.length;
                for (var i=0; i < length; i++) {
                    var tempNode = new YAHOO.widget.TextNode(
                        results.nodes[i], node, false);
                }
                oResponse.argument.fnLoadComplete();
            },
            failure: function(oResponse) {
                oResponse.argument.fnLoadComplete();
            },
            
            argument: {
                "node": node,
                "fnLoadComplete": fnLoadComplete
            },
            
            timeout: 7000
        };
        
        YAHOO.util.Connect.asyncRequest(
            'GET', "treeinfo?nodepath=" + nodepath, callback);

    };

    // expand the tree to a particular node and then execute fn
    var expandToNode = function(treeview, nodepath, fn) {
        var node = treeview.getRoot();
        var steps = nodepath.split('/').slice(1);
        expandToNodeHelper(nodepath, node, steps, fn);
    };
    
    // helper function to help asynchronously expand to a node
    var expandToNodeHelper = function(nodepath, node, steps, fn) {
        var step = steps[0];
        var next_steps = steps.slice(1);
        
        function expandCompleteHandler(node) {
            tree.unsubscribe("expandComplete");
            for (var i = 0; i < node.children.length; i++) {
                var child = node.children[i];
                if (nodepath.indexOf(child.data.path) == 0) {
                    if (next_steps.length == 0) {
                        fn(child);
                        return;
                    }
                    expandToNodeHelper(nodepath, child, 
                                       next_steps, fn);
                }
            }
        }
        
        if (!node.expanded) {
            tree.subscribe("expandComplete", expandCompleteHandler)
            node.expand();
        } else {
            expandCompleteHandler(node);
        }
    };

    // triggered when someone clicks on the back or forward button
    var nodepathStateChangeHandler = function(state) {
        if (YAHOO.util.Dom.get('location').innerHTML == state) {
            return;
        }
        expandToNode(tree, state, function(node) { 
            treeClick(node);
            tree.unsubscribe('expandComplete');
        });
    };

    // triggered upon reload
    var nodepathReadyHandler = function() {
        var nodepath = YAHOO.util.History.getCurrentState("nodepath");
        expandToNode(tree, nodepath, function(node) { 
            treeClick(node);
            tree.unsubscribe('expandComplete');
        });
    };
    
    // when someone someone clicks on a node in the tree
    var treeClick = function(node) {
        var nodepath = encodeURI(node.data.path);
        var tab = tabs.getTab(0);
        
        // XXX I wish I could simply change dataSrc attribute here, but that 
        // doesn't seem to refresh the tab content and I cannot figure out how. 
        // Changing the 'content' attribute does work.
        var callback = {
            success: function(oResponse) {
                tab.set('content', oResponse.responseText);
                YAHOO.util.Dom.get('location').innerHTML = nodepath;
                YAHOO.util.History.navigate("nodepath", node.data.path);
                tableInit(node.data.path);
                buttonsInit();
            },
            timeout: 7000
        };
        YAHOO.util.Connect.asyncRequest('GET', "tabinfo?nodepath=" + nodepath, 
                                        callback);
    };

    // initialize the tree
    var treeInit = function() {
        tree = new YAHOO.widget.TreeView("tree");
        tree.setDynamicLoad(loadNodeData);
      
        var root = tree.getRoot();
        var rootNode = new YAHOO.widget.TextNode(
            {label:"gegevens", path: getRootPath()}, 
            root, false);
        
        tree.subscribe("labelClick", treeClick);
        tree.draw();
    };

    // initialize the tabs
    var tabInit = function() {
        tabs = new YAHOO.widget.TabView("main");
        tabs.addTab(new YAHOO.widget.Tab({
           label: 'Browse',
           active: true
        }));
    };

    // initialize browser history functionality
    var historyInit = function() {
        var bookmarkedSection = YAHOO.util.History.getBookmarkedState(
            "nodepath");
        var initSection = bookmarkedSection || getRootPath();
        YAHOO.util.History.register("nodepath", initSection, 
                                    nodepathStateChangeHandler);
    };

    // initialize the table in the main browse tab
    // XXX currently this gets reinitialized each time someone browses
    var tableInit = function(nodepath) {
        var dataSource = new YAHOO.util.DataSource('tableinfo?nodepath=' + 
                                                   encodeURI(nodepath));
        dataSource.responseType = YAHOO.util.DataSource.TYPE_JSON;
        
        dataSource.responseSchema = {
            resultsList: "records",
            fields: ['name', 'title', 'path', 'container', 
                     'type', 'last_modified']
        };
        
        var columnDefs = [
            {key: 'name', label: "Name"},
            {key: 'title', label: "Title"},
            {key: 'type', label: "Type"},
            {key: 'last_modified', label: "Last modified"},
        ];
        
        datatable = new YAHOO.widget.DataTable('datatable', 
                                               columnDefs, dataSource);
        datatable.subscribe("rowClickEvent", rowClick);
    };

    // when someone clicks on a row in the table
    var rowClick = function(event, target) {
        var el = event.target;
        var data = datatable.getRecord(el).getData();

        if (!data.container) {
            // not a container, so select row
            datatable.onEventSelectRow(event, el);
            return;
        }

        // this is a container, so browse to path
        var nodepath = encodeURI(data.path);
        var tab = tabs.getTab(0);
        
        var callback = {
            success: function(oResponse) {
                tab.set('content', oResponse.responseText);
                YAHOO.util.Dom.get('location').innerHTML = nodepath;
                YAHOO.util.History.navigate("nodepath", data.path);
                tableInit(data.path);
                buttonsInit();
                expandToNode(tree, data.path, function(node) { 
                    tree.unsubscribe('expandComplete');
                });
            },
            timeout: 7000
        };
        
        YAHOO.util.Connect.asyncRequest('GET', "tabinfo?nodepath=" + nodepath, 
                                        callback);
    };

    // initialize button behavior on the screen
    // XXX should make this pluggable
    var buttonsInit = function() {
        var onSelectClick = function(event) {
            var rows = datatable.getSelectedRows();
            var paths = [];
            for (var i = 0; i < rows.length; i++) {
                paths.push(datatable.getRecord(rows[i]).getData().path);
            }
            window.relation_creator.setRelations(paths);
        };
        var onCancelClick = function(event) {
            window.close();
        };
        var selectButton = new YAHOO.widget.Button(
            {label:"Select",
             id:"selectButton",
             container:"buttons"});
        selectButton.on("click", onSelectClick);
        var cancelButton = new YAHOO.widget.Button(
            {label: "Cancel",
             id:"cancelButton",
             container:"buttons"});
        cancelButton.on("click", onCancelClick);
    };

    // retrieve the root path to start browsing
    var getRootPath = function() {
        return YAHOO.util.Dom.get('rootpath').getAttribute('rootpath');
    };
    
    //*** public functions
    PLOR.explorer.getTree = function() {
        return tree;
    };
    
    PLOR.explorer.getDataTable = function() {
        return datatable;
    };

    //*** initialization
    YAHOO.util.Event.onDOMReady(treeInit);
    YAHOO.util.Event.onDOMReady(tabInit);
    YAHOO.util.Event.onDOMReady(historyInit);
    
    YAHOO.util.History.onReady(nodepathReadyHandler);
    
    YAHOO.util.History.initialize("yui-history-field", "yui-history-iframe");
    
})();
