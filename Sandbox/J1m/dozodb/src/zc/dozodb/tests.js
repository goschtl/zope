
dojo.provide("zc.dozodb.tests");

dojo.registerModulePath('zc', '../../../src/zc/dozodb');

dojo.require("zc.dozodb");

zc.dozodb.tests = {
    name: 'zc.dozodb.tests',

    setUp: function () {
        this.old_xhr = dojo.xhr;
        this.old_xhrGet = dojo.xhrGet;
        dojo.xhr = dojo.hitch(
            this, function (method, args, hasBody) {
                this.xhr = { method: method, args: args, hasBody: hasBody};
            });
        dojo.xhrGet = function (args) {
            return dojo.xhr("GET", args);
        };
        dojo.xhrPost = function (args) {
            return dojo.xhr("POST", args, true);
        };
        this.xhr = null;
        this.store = zc.dozodb.Store({url: 'http://example.com/'});
    },

    checkGet: function (args) {
        doh.is(this.xhr.method, 'GET', 'method');
        doh.is(this.xhr.args.url, this.store.url, 'url');
        doh.is(this.xhr.args.handleAs, 'json', 'handleAs');
        doh.t(this.xhr.args.preventCache, 'preventCache');
        doh.f(this.xhr.hasBody, 'hasBody');
        this.xhr = null;
    },

    checkPost: function (args) {
        doh.is(this.xhr.method, 'POST', 'method');
        doh.is(this.xhr.args.url, this.store.url, 'url');
        doh.is(this.xhr.args.handleAs, 'json', 'handleAs');
        doh.t(this.xhr.args.preventCache, 'preventCache');
        doh.t(this.xhr.hasBody, 'hasBody');
        this.xhr = null;
    },

    test_interfaces: function () {
      doh.is(this.store.getFeatures(),
             {
                 'dojo.data.api.Read': true,
                 'dojo.data.api.Write': true,
                 'dojo.data.api.Identity': true,
                 'dojo.data.api.Notification': true
             });
    },

    test_close: function () {
        var onBeginCalled = false;
        var request = this.store.fetch(
            {
                onBegin: function () {onBeginCalled = true; }
            });
        this.store.close(request);
        this.xhr.args.load({items: []});
        doh.f(onBeginCalled);
        this.checkGet();
    },

    test_containsValue: function () {
        doh.f(this.store.containsValue({}, 'foo', 1));
        doh.f(this.store.containsValue({foo: 2}, 'foo', 1));
        doh.t(this.store.containsValue({foo: 1}, 'foo', 1));
        doh.t(this.store.containsValue({foo: [1]}, 'foo', 1));
        doh.t(this.store.containsValue({foo: [1, 2]}, 'foo', 1));
        doh.t(this.store.containsValue({foo: [2, 1]}, 'foo', 1));
        doh.f(this.store.containsValue({foo: [1]}, 'foo', [1]));
    },

    test_deleteItem: function () {
        var items;
        this.store.fetch(
            {
                onComplete: function (items_) {
                    items = items_;
                }
            });
        this.xhr.args.load({items: [{_p_oid: '1', x: 0, y: 0}]});
        var item1 = this.store.newItem({x: 1, y: 2});
        var item2 = this.store.newItem({x: 3, y: 4});
        var deleted = 0;
        dojo.connect(this.store, 'onDelete', function () { deleted++; });
        this.store.deleteItem(item1);
        this.store.deleteItem(items[0]);
        doh.is(deleted, 2);
        this.store.save();
        doh.is(
            dojo.fromJson(this.xhr.args.postData),
            { changed: [{_p_oid: "new1", x: 3 , y: 4}], inserted: ["new1"] }
        );
    },

    tearDown: function () {
        dojo.xhr = this.old_xhr;
        dojo.xhrGet = this.old_xhrGet;
    }
};

function registerSuite(ob) {

    function fixture(ob, name) {
        return {
            name: name,
            setUp: dojo.hitch(ob, ob.setUp),
            tearDown: dojo.hitch(ob, ob.tearDown),
            runTest: function () {
                try {
                    dojo.hitch(ob, ob[name])();
                    }
                catch (e) {
                    print(name + 'Failed.');
                    throw e;
                }
            }
        };
    }

    var tests = [];
    for (var name in ob)
        if (name.slice(0, 5) == 'test_')
            tests.push(fixture(ob, name));
    doh.registerTests(ob.name, tests);
}


registerSuite(zc.dozodb.tests);
