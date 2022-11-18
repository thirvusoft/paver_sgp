frappe.ui.form.on("Purchase Invoice", {
    onload_post_render: function (frm) {
        if (frm.is_new()) {
            frm.set_value("branch", "");
        }
        if (!frm.doc.branch) {
            frappe.db.get_list("Branch", { filters: { is_accounting: 1 } }).then(res => {
                if ((res || []).length > 0) {
                    frm.set_value("branch", res[0].name);
                }
            });
        }
    },
    taxes_and_charges: function (frm) {
        if (frm.doc.branch) {
            frappe.db.get_value("Branch", frm.doc.branch, "is_accounting").then((value) => {
                if (!value.message.is_accounting) {
                    if (frm.doc.taxes_and_charges) frm.set_value("taxes_and_charges", "");
                    if (frm.doc.tax_category) frm.set_value("tax_category", "");
                    if (frm.doc.taxes) frm.clear_table("taxes");
                    refresh_field("taxes");
                }
            });
        }
    },
    tax_category: function (frm) {
        frm.trigger("taxes_and_charges");
    },
    branch: function (frm) {
        frm.trigger("taxes_and_charges");
    },
    validate: function (frm) {
        frm.trigger("taxes_and_charges");
    },
});
