/** @odoo-module **/

import { PartnerDetailsEdit } from "@point_of_sale/app/screens/partner_list/partner_editor/partner_editor";
import { patch } from "@web/core/utils/patch";

patch(PartnerDetailsEdit.prototype, {
    setup() {
        const res = super.setup(...arguments);
        this.intFields.push('property_account_position_id', 'partner_document_type_id');
        const partner = this.props.partner;
        this.changes.property_account_position_id = partner.property_account_position_id && partner.property_account_position_id[0];
        this.changes.partner_document_type_id = partner.partner_document_type_id && partner.partner_document_type_id[0];
        return res;
    }
});
