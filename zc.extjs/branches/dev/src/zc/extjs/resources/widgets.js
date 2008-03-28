Ext.namespace('zc.extjs');

zc.extjs.widgets = function() {
    return {
        Field: function (widget)
        {
            var config;

            if (widget.widget_constructor)
                config = eval(widget.widget_constructor)(widget);
            else
                config = Ext.apply(widget, {})

            if (widget.fieldHint)
            {
                if (! config.listeners)
                    config.listeners = {};
                config.listeners.render = function (field) {
                    Ext.QuickTips.register({
                        target: field.getEl(),
                        title: widget.fieldLabel,
                        text: widget.fieldHint
                    });
                };
            }
            return config;
        },

        InputInt: function (widget)
        {
            var config = Ext.apply({xtype: 'textfield'}, widget);

            config.validator = function (value) {
                value = Number(value);
                if (config.field_min !== undefined && value < config.field_min)
                    return "The value must be at least "+config.field_min;
                if (config.field_max !== undefined && value > config.field_max)
                    return ("The value must be less than or equal to "
                            +config.field_max);
                return true;
            };
            if (config.field_min !== undefined && config.field_min >= 0)
                config.maskRe = /[0-9]/;
            else
            {
                config.maskRe = /[-0-9]/;
            }
            config.regex = /^-?[0-9]+$/;
            config.regexText = 'The input must be an integer.';
            return config;
        },

        InputDecimal: function (widget)
        {
            var config = Ext.apply({xtype: 'textfield'}, widget);

            config.validator = function (value) {
                value = Number(value);
                return !isNaN(value);
            };
            config.maskRe = /[-0-9.]/;
            config.regex = /^-?[0-9.]+$/;
            config.regexText = 'The input must be a decimal number.';
            return config;
        },

        InputChoice: function (widget)
        {
            var config = Ext.apply({xtype: 'combo'}, widget);

            if (config.values)
                config.store = new Ext.data.SimpleStore({
                    fields: [{name: 'value', mapping: 0},
                             {name: 'display', mapping: 1}
                            ],
                    id: 0,
                    data: config.values
                });
            config = Ext.apply(config, {
                valueField: 'value',
                displayField: 'display',
                triggerAction: 'all',
                selectOnFocus:true,
                editable: false,
                forceSelection: true,
                mode: 'local'
            });
            return config;
        }
    };    
}();
