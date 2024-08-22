/* @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {
    async onClickCreate() {
        let ctx = this.model.root.evalContext;
        if (!ctx.default_is_internal_transfer && ['outbound', 'inbound'].includes(ctx.default_payment_type) && this.model.root.resModel == 'account.payment') {
            return this.actionService.doAction({
                type: 'ir.actions.act_window',
                res_model: 'payment.imputation.wizard',
                views: [[false, 'form']],
                target: 'new',
                context: ctx
            });
        }
        return super.onClickCreate();
    },
});
