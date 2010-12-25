dojo.provide('zc.dozodb');

if (zc == null)
    zc = {};

zc.dozodb = function () {

    var empty = {};

    var Request = {
        aborted: false,
        constructor: function () {},
        abort: function () {
            this.aborted = true;
        }
    };
    Request = dojo.declare(null, Request);

    var Dozodb = {

        // url: url of data server

        constructor : function (args) {
            dojo.safeMixin(this, args);
            this._cache = {};       // {oid->ob}
            this._new_next = 0;
            this._new_ids = {};
        },

        _fixupItemSubobjects: function (item) {
            for (var name in item) {
                var v = item[name];
                if (typeof(v) != "object")
                    continue;
                var oid;
                try {
                    oid = v._p_oid;
                    }
                catch (e) {
                    oid = null;
                }
                if (oid)
                    item[name] = this._in_cache(v);
                this._fixupItemSubobjects(v);
            }
        },

        _in_cache: function (item, with_data) {
            if (item._p_oid in this._cache) {
                var cached = this._cache[item._p_oid];
                if (with_data)
                    dojo.safeMixin(cached, item);
                item = cached;
            }
            else
                this._cache[item._p_oid] = item;

            if (with_data) {
                this._fixupItemSubobjects(item);
                item._p_changed = false;
            }
            return item;
        },

        close : function (request) {
            request.abort();
        },

        containsValue : function (item, attribute, value) {
            var v = item[attribute];
            if (v == null)
                return false;
            if (v.length == null)
                return v == value;
            return dojo.indexOf(v, value) >= 0;
        },

        deleteItem : function (item) {
            // xxx
            this.onDelete(item);
        },
        onDelete: function (item) {}, // hook

        fetch : function (args) {
            var self = this;
            var request = new Request();
            dojo.xhrGet(
                {
                    // Server gets query args for args.query
                    // Server returns: {items: array_of_items}
                    url: self.url+'/fetch',
                    handleAs: 'json',
                    preventCache: true,
                    content: args.query,
                    load: function (r) {
                        if (request.aborted)
                            return;
                        var items = dojo.map(
                            r.items,
                            function (item) {
                                return self._in_cache(item, true);
                            });
                        if (args.onBegin) {
                            dojo.hitch(args.scope, args.onBegin)(
                                items.length, request);
                            if (request.aborted)
                                return;
                        }
                        if (args.onItem) {
                            var f = dojo.hitch(args.scope, args.onItem);
                            for (var i=0; i < items.length; i++) {
                                f(items[i], request);
                                if (request.aborted)
                                    return;
                            }
                            if (args.onComplete)
                                dojo.hitch(args.scope, args.onComplete)(
                                    null, request);
                        }
                        else if (args.onComplete)
                        dojo.hitch(args.scope, args.onComplete)(
                                items, request);
                    },
                    error: function (e) {
                        if (request.aborted)
                            return;
                        if (args.onError)
                            dojo.hitch(args.scope, args.onError)(
                                e, request);
                        else
                            alert(e);

                    }
                });
            return request;
        },

        fetchBydentity : function (args) {
            if (args.identity in self._cache) {
                if (args.onItem)
                    dojo.hitch(args.scope, args.onItem)(
                        self._cache[args.identity]);
                return;
            }
            self = this;
            dojo.xhrGet(
                {
                    // Server gets query arg _p_oid
                    // Server returns: {item: item}
                    url: this.url+'/fetchBydentity',
                    handleAs: 'json',
                    preventCache: true,
                    content: {_p_oid: args.identity},
                    load: function (r) {
                        var item = self._in_cache(r.item, true);
                        if (args.onItem)
                            dojo.hitch(args.scope, args.onItem)(item);
                    },
                    error: (args.onError
                            ? dojo.hitch(args.scope, args.onError)
                            : alert)
                });
        },

        getAttributes : function (item) {
            var result = [];
            for (var name in item)
                if ((!(name in empty)) && name.slice(0, 1) != '_')
                    result.push(name);
        },

        getFeatures : function () {
            return {
                'dojo.data.api.Read': true,
                'dojo.data.api.Write': true,
                'dojo.data.api.Identity': true,
                'dojo.data.api.Notification': true
            };
        },

        getIdentity: function (item) {
            return item._p_oid;
        },

        getIdentityAttributes: function (item) {
            return ['_p_oid'];
        },

        getLabel : function (item) {
            // replace me :)
            return item.title || item.label || item._p_oid || 'unlabeled';
        },

        getValue : function (item, attribute, defaultValue) {
            if (attribute in item)
                return item[attribute];
            return defaultValue;
        },

        getValues : function (item, attribute) {
            var v = this.getValue(item, attribute, []);
            if (v.length == null)
                v = [v];
            return v;
        },

        hasAttribute : function (item, attribute) {
            return item[attribute] != null;
        },

        isDirty : function (item) {
            return item._p_changed == true;
        },

        isItem : function (v) {
            return v._p_jar === this;
        },

        isItemLoaded : function (item) {
            return item._p_changed != null;
        },

        loadItem : function (args) {
            var item = args.item;
            console.log('loading '+item._p_oid);
            if (item._p_changed != null) {
                if (args.onItem != null)
                    dojo.hitch(args.scope, args.onItem)(item);
                return;
            }
            self = this;
            dojo.xhrGet(
                {
                    // Server gets query arg _p_oid
                    // Server returns: {item: item}
                    url: this.url+'/load',
                    handleAs: 'json',
                    preventCache: true,
                    content: {_p_oid: item._p_oid},
                    load: function (r) {
                        dojo.safeMixin(item, r.item);
                        item._p_changed = false;
                        self._fixupItemSubobjects(item);
                        if (args.onItem)
                            dojo.hitch(args.scope, args.onItem)(item);
                    },
                    error: (args.onError
                            ? dojo.hitch(args.scope, args.onError)
                            : alert)
                });
        },

        newItem : function (args, parentInfo) {
            var item = dojo.safeMixin(
                {_p_oid: 'new'+this._new_next++, _p_changed: 0}, args);
            if (parentInfo) {
                var v = parentInfo.parent[parentInfo.attribute];
                if (v == null || v.length == null)
                    parentInfo.parent[parentInfo.attribute] = item;
                else
                    v.push(item);
            }
            this.onNew(
                item, {
                    item: parentInfo.parent,
                    attribute: parentInfo.attribute
                });
            return item;
        },
        onNew: function (item, parentInfo) {}, // hook

        revert : function () {

        },

        save : function (args) {

        },

        setValue : function (item, attribute, value) {
            var old = undefined;
            if (attribute in item)
                old = attribute[item];
            if (old == null || old.length == null)
                item[attribute] = value;
            else
                item[attribute] = [value];
            this.onSet(item, attribute, old, value);
        },

        setValues : function (item, attribute, value) {
            var old = undefined;
            if (attribute in item)
                old = item[attribute];
            if (value == [])
                delete item[attribute];
            else
                item[attribute] = value;
            this.onSet(item, attribute, old, value);
        },
        onSet: function (item, attribute, old, new_) {}, // hook

        unsetAttribute : function (item, attribute) {
            delete item[attribute];
        }
    };

    return {
        DB: dojo.declare(null, Dozodb)
    };
}();
