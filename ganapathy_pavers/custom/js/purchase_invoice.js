var date
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
                    frm.set_value("apply_tds", 0);
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
    refresh: function (frm) {
        if (frm.doc.docstatus != 2 && frm.doc.purpose != "Service" && frm.doc.vehicle) {
            frm.add_custom_button("Vehicle Log", function () {
                create_vehicle_log(frm)
            }, "Create");
        }
    },
    on_submit: function(frm) {
        if (cur_frm.tags.tags.tagsList.length===0) {
            scroll_to_tags()
        }
    }
});

async function create_vehicle_log(frm) {
    date = cur_frm.doc.posting_date
    if (frm.doc.vehicle) {
        await frappe.run_serially([
            async () => {
                await frappe.new_doc("Vehicle Log", {
                    select_purpose: frm.doc.purpose,
                    date: date,
                    purchase_invoice: frm.doc.name,
                    license_plate: frm.doc.vehicle
                });
            },
            () => {
                cur_frm.set_value("date", date)
            }
        ]);
    } else {
        let d = new frappe.ui.Dialog({
            title: "Vehicle Log Details",
            fields: [
                {
                    fieldname: "vehicle",
                    fieldtype: "Link",
                    options: "Vehicle",
                    label: "Vehicle",
                    reqd: 1,
                },
                {
                    fieldname: "purpose",
                    fieldtype: "Select",
                    options:"\nRaw Material\nService",
                    label: "Purpose",
                    reqd: 1,
                }
            ],
            primary_action: async function (data) {
                await frappe.db.set_value(frm.doc.doctype, frm.doc.name, "vehicle", data.vehicle);
                await frappe.db.set_value(frm.doc.doctype, frm.doc.name, "purpose", data.purpose);
                await frm.reload_doc();
                await frappe.run_serially([
                    async () => {
                        await frappe.new_doc("Vehicle Log", {
                            select_purpose: data.purpose,
                            date: date,
                            purchase_invoice: frm.doc.name,
                            license_plate: data.vehicle
                        });
                    },
                    () => {
                        cur_frm.set_value("date", date)
                    }
                ]);
            }
        });
        d.show()
    }
}

function scroll_to_tags() {
    let $el = cur_frm.tags.wrapper[0];
    frappe.utils.scroll_to($el, true, 15);
    $el.style.border="1px solid red"
    setTimeout(() => {
        $el.style.border="";
        $el.focus();
    }, 1000);
}