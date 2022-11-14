frappe.ui.form.on("Quotation", {
    party_name: async function (frm) {
        if (frm.doc.quotation_to == "Lead" && frm.doc.party_name) {
            await frappe.db.get_value("Lead", frm.doc.party_name, "type").then(res => {
                frm.set_value("order_type", res["message"]["type"])
            })
        }
    },
    before_validate: function (frm) {
        if (!frm.doc.order_type) {
            frm.trigger("party_name")
        }
    },
    onload: function (frm) {
        if (frm.is_new() && !frm.doc.order_type) {
            frm.trigger("party_name")
        }
    },
})