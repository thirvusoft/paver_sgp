// Copyright (c) 2022, Thirvusoft and contributors
// For license information, please see license.txt
var dialog1, dialog2;
frappe.ui.form.on("Daily Stock Maintenance", {
    refresh: async function (frm) {
        if (frm.is_new()) {
            let attr = [],
                attr_fields = [
                    {
                        fieldname: "item",
                        label: "Item",
                        fieldtype: "Data",
                        in_list_view: 1,
                        columns: 1,
                    },
                ];
            await frappe.db
                .exists("Item Attribute", "Colour")
                .then((result) => {
                    if (result) {
                        frappe.db.get_doc("Item Attribute", "Colour").then((attr_doc) => {
                            (attr_doc.item_attribute_values || []).forEach((row) => {
                                if (row.attribute_value && !attr.includes(row.attribute_value)) {
                                    attr.push(row.attribute_value);
                                    attr_fields.push({
                                        fieldname: (row.attribute_value || "").toLowerCase(),
                                        label: row.attribute_value,
                                        fieldtype: "Data",
                                        in_list_view: 1,
                                        columns: 1,
                                    });
                                }
                            });
                        });
                    }
                })
                .then(() => {
                    dialog1 = new frappe.ui.Dialog({
                        fields: [
                            {
                                fieldname: "normal_paver1",
                                fieldtype: "Table",
                                label: "Normal Paver Stock",
                                fields: attr_fields,
                            },
                        ],
                    });
                    dialog2 = new frappe.ui.Dialog({
                        fields: [
                            {
                                fieldname: "shot_blast1",
                                fieldtype: "Table",
                                label: "Shot Blast Paver Stock",
                                fields: attr_fields,
                            },
                        ],
                    });
                    frm.set_df_property("normal_paver_stock", "options", dialog1.wrapper[0]);
                    frm.set_df_property("shot_blast_paver_stock", "options", dialog2.wrapper[0]);
                });
        }
    },
    validate: function (frm) {
        if (dialog1 && dialog1.fields_dict && dialog1.fields_dict.normal_paver1 && dialog1.fields_dict.normal_paver1.grid && dialog1.fields_dict.normal_paver1.grid.data) {
            frm.set_value("normal_paver_stock_list", dialog1.fields_dict.normal_paver1.grid.data);
        } else {
            frm.set_value("normal_paver_stock_list", []);
        }

        if (dialog2 && dialog2.fields_dict && dialog2.fields_dict.shot_blast1 && dialog2.fields_dict.shot_blast1.grid && dialog2.fields_dict.shot_blast1.grid.data) {
            frm.set_value("shot_blast_paver_stock_list", dialog2.fields_dict.shot_blast1.grid.data);
        } else {
            frm.set_value("shot_blast_paver_stock_list", []);
        }
    },
});
