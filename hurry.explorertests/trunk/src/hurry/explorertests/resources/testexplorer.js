(function() {
var explorerTestCase = new YAHOO.tool.TestCase({
    name: "Explorer testcase",

    // expand the top node and see whether we get the expected
    // content
    testExpand: function() {
        var tree = PLOR.explorer.getTree();
        var Assert = YAHOO.util.Assert;
        var subscribeHandler = function() {
            tree.unsubscribe("expandComplete", subscribeHandler);
            this.resume(function() {
                var top = tree.getRoot().children[0];
                Assert.areEqual("a", top.children[0].data.label);
                Assert.areEqual("b", top.children[1].data.label);
            });
        }
        tree.subscribe("expandComplete", subscribeHandler, this, true);
        tree.collapseAll();
        tree.getRoot().children[0].expand();
        this.wait();
    },

    // expand the 'a' node and see whether we get the expected
    // content
    testExpand2: function() {
        var tree = PLOR.explorer.getTree();
        var Assert = YAHOO.util.Assert;
        // when we expand top node
        var top = tree.getRoot().children[0];
        var subscribeHandler = function() {
            tree.unsubscribe("expandComplete", subscribeHandler);
            // when we expand the 'a' node
            var a = top.children[0];
            var innerSubscribeHandler = function() {
                tree.unsubscribe("expandComplete", innerSubscribeHandler);
                this.resume(function() {
                    Assert.areEqual("c", a.children[0].data.label);
                    Assert.areEqual("d", a.children[1].data.label);
                });
            };
            tree.subscribe("expandComplete", innerSubscribeHandler, 
                           this, true);
            a.expand();
        };

        tree.subscribe("expandComplete", subscribeHandler, this, true);
        tree.collapseAll();
        top.expand();
        this.wait();
    },

    // click on the 'a' node and see whether the contents is correct
    testClick: function() {
        var Assert = YAHOO.util.Assert;
        var tree = PLOR.explorer.getTree();

        var top = tree.getRoot().children[0];
        var sub = function() {
            tree.unsubscribe("expandComplete", sub);
            var a = top.children[0];
            YAHOO.util.UserAction.click(a.getLabelEl());
        };
        tree.subscribe("expandComplete", sub, this, true);
        tree.collapseAll();
        top.expand();
        // XXX ugh, have to wait half a second to load data and
        // hope it is enough...
        this.wait(function() {
            var table = PLOR.explorer.getDataTable();
            Assert.areEqual("c", table.getRecord(0).getData().name);
            Assert.areEqual("d", table.getRecord(1).getData().name);
        }, 500);
    }
});

var suite = new YAHOO.tool.TestSuite("Explorer testsuite");
suite.add(explorerTestCase);

YAHOO.util.Event.onDOMReady(function() {
  var logger = new YAHOO.tool.TestLogger();
  YAHOO.tool.TestRunner.add(suite);
  YAHOO.tool.TestRunner.run();
});

})();
