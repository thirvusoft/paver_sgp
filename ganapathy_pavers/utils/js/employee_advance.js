frappe.ui.form.on("Employee Advance", {
    refresh: function (frm) {
        let originalSave = frm.validate_and_save
        frm.validate_and_save = function (...args) {
            calculate_deduction_planning(frm)
            originalSave.call(frm, ...args)
        }
        frappe.route_hooks.after_submit = () => frm.trigger("after_submit");
    },
    after_submit: function (frm) {
        frm.reload_doc();
    }
})

frappe.ui.form.on("Deduction Planning", {
    amount: function (frm, cdt, cdn) {
        calculate_deduction_planning(frm, cdt, cdn);
    },
    deduction_planning_add: function (frm, cdt, cdn) {
        calculate_deduction_planning(frm, cdt, cdn);
    },
    deduction_planning_remove: function (frm, cdt, cdn) {
        calculate_deduction_planning(frm, cdt, cdn);
    },
});

function calculate_deduction_planning(frm, cdt, cdn) {
    if (frm.doc.docstatus !== 1) {
        return;
    }
    let total_amount = 0;
    (frm.doc.deduction_planning || []).forEach(row => {
        total_amount += (row.amount || 0)
    });
    if (total_amount > frm.doc.advance_amount) {
        frappe.throw({ message: "<b>Total Planned Deduction amount</b> can't be greater than <b>Advance Amount</b>", indicator: "red" });
        return;
    }
    frm.set_value("total_planned_deductions", total_amount);
}
