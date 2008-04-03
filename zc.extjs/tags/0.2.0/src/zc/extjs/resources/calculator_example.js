Ext.namespace('zc.extjs');

zc.extjs.calculator_example = function () {

    function init () {
        var input = new Ext.form.TextField({
            id: 'input',
            maskRe: /[0-9]/,
            value: 1
        });

        function setValue(result)
        {
            Ext.get('value').dom.innerHTML = result.value;
        }

        zc.extjs.util.call_server({
            url: 'value',
            task: 'Getting value',
            success: setValue
        });

        new Ext.Viewport({
            items: [
                {xtype: 'box', autoEl: 
                 {
                     tag: 'div', 
                     html: 'Current value: <span id="value">?</span><br>'}
                },
                {xtype: 'box', autoEl: {tag: 'span', html: 'Input:'}},
                input,
                new Ext.Button({
                    text: '+', id: 'add-button',
                    handler: function () {
                        zc.extjs.util.call_server({
                            url: 'add',
                            params: {'value:int': input.getValue()},
                            task: 'Adding',
                            success: setValue
                        });
                    }
                }),
                new Ext.Button({
                    text: '-', id: 'subtract-button',
                    handler: function () {
                        zc.extjs.util.call_server({
                            url: 'subtract',
                            params: {'value:int': input.getValue()},
                            task: 'Subtracting',
                            success: setValue
                        });
                    }
                })
            ]
        })
    }

    return {
        init: init
    };

} ();

Ext.onReady(zc.extjs.calculator_example.init);
