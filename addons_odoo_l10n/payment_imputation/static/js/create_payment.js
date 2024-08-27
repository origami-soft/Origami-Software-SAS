odoo.define('payment_imputation.create_payment_wizard', function(require){

    var ListController = require('web.ListController');

    ListController.include({
        _onCreateRecord: function (ev) {
            if (this.$buttons && this.$buttons.find('#payment_imputation').length && this.initialState.context.default_payment_type != 'transfer') {
                this.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'payment.imputation.wizard',
                    views: [[false, 'form']],
                    target: 'new',
                    context: this.initialState.context
                });
            }else{
                this._super.apply(this, arguments);
            }
        },
    });
});
