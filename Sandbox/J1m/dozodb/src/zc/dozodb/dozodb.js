dojo.provide('zc.dozodb');

if (zc === undefined)
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

    var idattrs = {_p_oid: true, _p_id: true};

    function list(obj) {
        var r = [];
        for (var name in obj)
            if (obj.hasOwnProperty(name))
                r.push(name);
        return r;
    }

    var Dozodb = {

        // url: url of data server

        constructor : function (args) {
            dojo.safeMixin(this, args);
            this._cache = {};       // {oid->ob}
            this._new_next = 0;
            this._initialize_changes();
        },

        _initialize_changes: function () {
            this._changes = {changed: {}, inserted: {}};
        },

        _convert_incoming_items_refs_to_items: function (item) {
            for (var name in item) {
                var v = item[name];
                if (typeof(v) !== "object")
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
                this._convert_incoming_items_refs_to_items(v);
            }
        },

        _convert_outgoing_items_to_item_refs: function (item, isobject) {
            var maybe_array = (! isobject) && (item.length !== undefined);
            var result;
            if (maybe_array) {
                result = [];
            }
            else {
                result = {};
            }

            for (var name in item) {
                if (! item.hasOwnProperty(name))
                    continue;

                if (maybe_array && name === 'length')
                    return _convert_outgoing_items_to_item_refs(item, true);

                var v = item[name];
                if (typeof(v) !== "object") {
                    result[name] = v;
                    continue;
                }
                var oid;
                try {
                    oid = v._p_id;
                    }
                catch (e) {
                    oid = null;
                }
                if (oid) {
                    result[name] = {_p_ref: oid};
                    continue;
                }
                result[name] = this._convert_outgoing_items_to_item_refs(v);
            }
            return result;
        },

        _in_cache: function (item, with_data) {
            if (! item._p_id)
                item._p_id = item._p_oid;
            if (item._p_id in this._cache) {
                var cached = this._cache[item._p_id];
                if (with_data)
                    dojo.safeMixin(cached, item);
                item = cached;
            }
            else
                this._cache[item._p_id] = item;

            if (with_data) {
                this._convert_incoming_items_refs_to_items(item);
                item._p_changed = false;
            }
            return item;
        },

        close : function (request) {
            request.abort();
        },

        containsValue : function (item, attribute, value) {
            var v = item[attribute];
            if (v === undefined)
                return false;
            if (v.length === undefined)
                return v === value;
            for (var i=v.length; --i >= 0; )
                if (v[i] === value)
                    return true;
            return false;
        },

        deleteItem : function (item) {
            if (! item._p_oid) {
                // New object
                delete this._changes.changed[item._p_id];
                if (item._p_id in this._changes.inserted)
                    delete this._changes.inserted[item._p_id];
            }
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
                    url: self.url,
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
                                r.size || -1, request);
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
                            if (args.onComplete) {
                                dojo.hitch(args.scope, args.onComplete)(
                                    null, request);
                            }
                        }
                        else if (args.onComplete) {
                            dojo.hitch(args.scope, args.onComplete)(
                                items, request);
                        }
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
                    url: this.url,
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
                if ((!(name in empty)) && name.slice(0, 1) !== '_')
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
            return item._p_id;
        },

        getIdentityAttributes: function (item) {
            return ['_p_id'];
        },

        getLabel : function (item) {
            // replace me :)
            return item.title || item.label || item._p_id || 'unlabeled';
        },

        getValue : function (item, attribute, defaultValue) {
            if (attribute in item)
                return item[attribute];
            return defaultValue;
        },

        getValues : function (item, attribute) {
            var v = this.getValue(item, attribute, []);
            if (v.length === undefined)
                v = [v];
            return v;
        },

        hasAttribute : function (item, attribute) {
            return item[attribute] !== undefined;
        },

        isDirty : function (item) {
            return item._p_changed === true;
        },

        isItem : function (v) {
            return v._p_jar === this;
        },

        isItemLoaded : function (item) {
            return item._p_changed !== undefined;
        },

        loadItem : function (args) {
            var item = args.item;
            if (item._p_changed !== undefined) {
                if (args.onItem !== undefined)
                    dojo.hitch(args.scope, args.onItem)(item);
                return;
            }
            self = this;
            console.log('loading '+item._p_oid);
            dojo.xhrGet(
                {
                    // Server gets query arg _p_oid
                    // Server returns: {item: item}
                    url: this.url,
                    //sync: true,
                    handleAs: 'json',
                    preventCache: true,
                    content: {_p_oid: item._p_oid},
                    load: function (r) {
                        console.log('loaded '+item._p_oid);
                        dojo.safeMixin(item, r.item);
                        item._p_changed = false;
                        self._convert_incoming_items_refs_to_items(item);
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
                {_p_id: 'new'+this._new_next++, _p_changed: 1}, args);
            if (parentInfo) {
                var parent = parentInfo.parent;
                if (item._p_changed === undefined)
                    throw("Attempt to modify ghost parent.");
                var v = parent[parentInfo.attribute];
                if (v === undefined || v.length === undefined)
                    parent[parentInfo.attribute] = item;
                else
                    v.push(item);
                this._changes.changed[parent._p_id] = parent;
            }
            else
                this._changes.inserted[item._p_id] = 1;
            this._cache[item._p_id] = item;
            this._changes.changed[item._p_id] = item;
            if (parentInfo)
                this.onNew(
                    item, { item: parent, attribute: parentInfo.attribute });
            else
                this.onNew(item);
            return item;
        },
        onNew: function (item, parentInfo) {}, // hook

        revert : function () {
            for (var id in self._changes.changed) {
                var item = self._changes.changed[id];
                if (item._p_oid) {
                    var _p_oid = item._p_oid;
                    for (var name in item)
                        if (item.hasOwnProperty(name) && ! name in ids)
                            delete item[name];
                }
                else
                {
                    delete self._cache[id];
                }
            }
            self._initialize_changes();
        },

        _to_save: function () {
            self = this;
            return dojo.toJson(
                {
                    changed: dojo.map(
                        list(self._changes.changed),
                        function (id) {
                            var r = self._convert_outgoing_items_to_item_refs(
                                self._changes.changed[id], true);
                            r._p_oid = r._p_id;
                            delete r._p_id;
                            delete r._p_changed;
                            return r;
                        }),
                    inserted: list(self._changes.inserted)
                });
        },

        save : function (args) {
            self = this;
            dojo.xhrPost(
                {
                    url: this.url,
                    handleAs: 'json',
                    headers: {'Content-Type': 'application/json'},
                    postData: self._to_save(),
                    load: function (r) {
                        self._initialize_changes();
                        for (var i=r.updates.length; --i >= 0; ) {
                            var data = r.updates[i];
                            if ('_p_id' in data) {
                                self._cache[data._p_oid] = self._cache[
                                    data._p_id];
                                delete data._p_id;
                            }
                            var item = self._cache[data._p_oid];
                            for (var name in data)
                                if (data.hasOwnProperty(name))
                                    item[name] = data[name];
                        }
                    }
                });
        },

        setValue : function (item, attribute, value) {
            if (item._p_changed === undefined)
                throw("Attempt to modify ghost.");

            var old = item[attribute];
            if (old === value)
                return true;

            item[attribute] = value;
            item._p_changed = true;
            this._changes.changed[item._p_id] = item;
            this.onSet(item, attribute, old, value);
            return true;        // I guess :/
        },
        setValues : function (item, attribute, value) {
            if (dojo.isArray(value) && value.length === 0)
                return this.unsetAttribute(item, attribute);
            return this.setValue(item, attribute, value);
        },
        onSet: function (item, attribute, old, new_) {}, // hook

        unsetAttribute : function (item, attribute) {
            if (item._p_changed === undefined)
                throw("Attempt to modify ghost.");

            if (attribute in item) {
                var old = item[attribute];
                delete item[attribute];
                item._p_changed = true;
                this._changes.changed[item._p_id] = item;
                self.onset(item, attribute, old, undefined);
            }
            return true;
        }
    };

    return {
        Store: dojo.declare(null, Dozodb)
    };
}();
