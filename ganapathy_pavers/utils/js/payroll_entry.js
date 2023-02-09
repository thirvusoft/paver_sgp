frappe.ui.form.on("Payroll Entry", {
    refresh: async function (frm) {
        if (frm.doc.docstatus === 1 && (await frappe.db.get_list("Salary Slip", {
            filters: {
                payroll_entry: frm.doc.name,
                docstatus: ["!=", 2]
            }
        })).length===0) {
            cur_frm.remove_custom_button("Submit Salary Slip");
            cur_frm.add_custom_button("Create Salary Slips", function () {
                frappe.call({
                    method: "ganapathy_pavers.utils.py.payroll_entry.create_salary_slips_from_pe",
                    args: {
                        name: frm.doc.name
                    }
                });
            }).addClass("btn-primary").removeClass("btn-default");
        }
    }
});