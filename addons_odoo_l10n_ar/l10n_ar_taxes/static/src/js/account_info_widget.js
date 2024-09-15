/** @odoo-module **/

import { registry } from "@web/core/registry";
import { usePopover } from "@web/core/popover/popover_hook";
import { useService } from "@web/core/utils/hooks";
import { localization } from "@web/core/l10n/localization";

import { formatMonetary } from "@web/views/fields/formatters";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

class AccountMoveShowAmountInfoPopOver extends Component {}
AccountMoveShowAmountInfoPopOver.props = {
    "*": { optional: true },
}
AccountMoveShowAmountInfoPopOver.template = "l10n_ar_taxes.AccountMoveShowAmountInfoPopOver";

export class AccountMoveShowAmountInfoField extends Component {
    static props = {...standardFieldProps};

    setup() {
        const position = localization.direction === "rtl" ? "bottom" : "left";
        this.popover = usePopover(AccountMoveShowAmountInfoPopOver, {position});
        this.orm = useService("orm");
        this.action = useService("action");
    }

    getInfo() {
        const info = this.props.record.data[this.props.name] || {
            content: [],
            title: "",
            move_id: this.props.record.resId,
        };

        for (const [key, value] of Object.entries(info.content)) {
            value.amount_to_tax_formatted = formatMonetary(value.amount_to_tax, {
                currencyId: value.currency_id,
            });
            value.amount_not_taxable_formatted = formatMonetary(value.amount_not_taxable, {
                currencyId: value.currency_id,
            });
            value.amount_exempt_formatted = formatMonetary(value.amount_exempt, {
                currencyId: value.currency_id,
            });

        }
        return {
            lines: info.content,
            title: info.title,
            moveId: info.move_id,
        };
    }

    onInfoClick(ev, line) {
        this.popover.open(ev.currentTarget, {
            title: "Información sobre los importes",
            ...line
        });
    }
}

AccountMoveShowAmountInfoField.template = "l10n_ar_taxes.AccountMoveShowAmountInfoField";

export const accountShowInfoField = {
    component: AccountMoveShowAmountInfoField,
    supportedTypes: ["char"],
};

registry.category("fields").add("showInfoMove", accountShowInfoField);