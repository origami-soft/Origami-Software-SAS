odoo.define('account.invoice.info', function (require) {
"use strict";

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var QWeb = core.qweb;
var field_registry = require('web.field_registry');


var ShowAmountInfoWidget = AbstractField.extend({
    supportedFieldTypes: ['char'],

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @override
     * @returns {boolean}
     */
    isSet: function() {
        return true;
    },

    /**
     * @private
     * @override
     */
    _render: function() {
        var self = this;
        var info = JSON.parse(this.value);
        if (!info) {
            this.$el.html('');
            return;
        }
        this.$el.html(QWeb.render('ShowAmountInfo', {
            title: info.title
        }));

        _.each(this.$('.js_amount_info'), function(k, v){
            var content = info.content[v];
            var options = {
                content: function() {
                    return $(QWeb.render('AmountPopOver', {
                        amount_to_tax: content.amount_to_tax,
                        amount_not_taxable: content.amount_not_taxable,
                        amount_exempt: content.amount_exempt,
                        currency: content.currency,
                        position: content.position,
                    }));
                },
                html: true,
                placement: 'left',
                title: 'Informacion de importes',
                trigger: 'focus',
                delay: { "show": 0, "hide": 100 },
                container: $(k).parent(),
            };
            $(k).popover(options);
        });
    },

});

field_registry.add('amountinfo', ShowAmountInfoWidget);

return {
    ShowAmountInfoWidget: ShowAmountInfoWidget
};

});