/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    //@override
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.document_types = loadedData["partner.document.type"];
    },
});

