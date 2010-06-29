dojo.require('dijit.Tree');
dojo.require("dojo.data.ItemFileReadStore");
dojo.require("dijit.layout.ContentPane");
dojo.require("dijit.layout.BorderContainer");
     

dojo.addOnLoad((function () {

    var store = new dojo.data.ItemFileReadStore({ url: "api.json"});

    var treeModel = new dijit.tree.TreeStoreModel({
        store: store,
        query: { id: 'root' },
        rootId: "root"
    });
    var div = dojo.create('div',{}, dojo.body());
    var border = new dijit.layout.BorderContainer({
        style: 'width: 100%; height: 100%',
        liveSplitters: true
    });
    div.appendChild(border.domNode);
    border.addChild(
        new dijit.layout.ContentPane({
            content: new dijit.Tree({
                model: treeModel,
                onClick: function (node) {
                    if (node.url[0])
                        iframe.src = 'http://dojotoolkit.org'+node.url[0];
                }
            }, "treeOne"),
            style: 'width: 20em',
            splitter: true,
            region:  'left'
        })
    );
    border.addChild(
        new dijit.layout.ContentPane({
            region: 'center'
        })
    );
    var iframe = dojo.create('iframe', {
        style: 'width: 100%; height: 99%'
    }, border.getChildren()[1].containerNode);
    border.startup();
    border.layout();
}));
